//! regen-cas: Content-Addressable Storage
//! Store files once, retrieve by content hash

use clap::{Parser, Subcommand};
use opendal::Operator;
use opendal::services::Fs;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use twox_hash::{xxh3::xxh3_128, Twox128};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CasEntry {
    pub address: String,
    pub original_name: String,
    pub mime_type: String,
    pub size_original: u64,
    pub size_stored: u64,
    pub created_at: i64,
    pub tags: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Default)]
struct Index {
    entries: HashMap<String, CasEntry>,
}

fn compute_address(data: &[u8]) -> String {
    hex::encode(xxh3_128(data))
}

fn compress(data: &[u8]) -> Vec<u8> {
    lz4_flex::compress_prepend_size(data)
}

fn decompress(data: &[u8]) -> Result<Vec<u8>, String> {
    lz4_flex::decompress_size_prepended(data)
        .map_err(|e| format!("Decompression failed: {}", e))
}

fn detect_mime(data: &[u8]) -> String {
    // Simple magic byte detection
    if data.starts_with(&[0x89, 0x50, 0x4E, 0x47]) {
        return "image/png".to_string();
    }
    if data.starts_with(&[0xFF, 0xD8, 0xFF]) {
        return "image/jpeg".to_string();
    }
    if data.starts_with(b"%PDF") {
        return "application/pdf".to_string();
    }
    if data.starts_with(b"<!DOCTYPE") || data.starts_with(b"<html") {
        return "text/html".to_string();
    }
    "application/octet-stream".to_string()
}

fn get_index(op: &Operator) -> Result<Index, String> {
    let data = op.read("index.json").await;
    match data {
        Ok(bytes) => {
            let s = String::from_utf8_lossy(&bytes);
            serde_json::from_str(&s).map_err(|e| e.to_string())
        }
        Err(_) => Ok(Index::default()),
    }
}

fn save_index(op: &Operator, index: &Index) -> Result<(), String> {
    let s = serde_json::to_string_pretty(index).map_err(|e| e.to_string())?;
    op.write("index.json", s).await.map_err(|e| e.to_string())
}

#[derive(Parser)]
#[command(name = "regen-cas")]
#[command(about = "Content-Addressable Storage")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Store a file, returns address
    Store { file: PathBuf },
    /// Retrieve file by address
    Get { address: String },
    /// List all stored files
    List,
    /// Find by tag
    Find { tag: String },
    /// Show storage stats
    Stats,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let root = std::env::var("REGEN_CAS_ROOT").unwrap_or_else(|_| "/data/cas".to_string());
    
    let mut fs = Fs::default();
    fs.root(&root);
    let op = Operator::new(fs).finish()?;

    match cli.command {
        Commands::Store { file } => {
            let data = std::fs::read(&file).map_err(|e| e.to_string())?;
            let address = compute_address(&data);
            let size_original = data.len() as u64;
            
            // Check if already exists
            let mut index = get_index(&op).await?;
            if let Some(entry) = index.entries.get(&address) {
                println!("{{\"address\":\"{}\",\"size\":{},\"duplicate\":true}}", 
                    entry.address, entry.size_original);
                return Ok(());
            }
            
            // Compress and store
            let compressed = compress(&data);
            op.write(&address, compressed).await.map_err(|e| e.to_string())?;
            
            // Update index
            let entry = CasEntry {
                address: address.clone(),
                original_name: file.file_name()
                    .map(|n| n.to_string_lossy().to_string())
                    .unwrap_or_default(),
                mime_type: detect_mime(&data),
                size_original,
                size_stored: compressed.len() as u64,
                created_at: chrono::Utc::now().timestamp(),
                tags: vec![],
            };
            index.entries.insert(address.clone(), entry);
            save_index(&op, &index).await?;
            
            println!("{{\"address\":\"{}\",\"size\":{}}}", address, size_original);
        }
        
        Commands::Get { address } => {
            let data = op.read(&address).await.map_err(|e| e.to_string())?;
            let decompressed = decompress(&data)?;
            std::io::Write::write_all(&mut std::io::stdout(), &decompressed)?;
        }
        
        Commands::List => {
            let index = get_index(&op).await?;
            println!("{}", serde_json::to_string_pretty(&index.entries)?);
        }
        
        Commands::Find { tag } => {
            let index = get_index(&op).await?;
            let results: Vec<_> = index.entries.values()
                .filter(|e| e.tags.contains(&tag))
                .collect();
            println!("{}", serde_json::to_string_pretty(&results)?);
        }
        
        Commands::Stats => {
            let index = get_index(&op).await?;
            let total_original: u64 = index.entries.values().map(|e| e.size_original).sum();
            let total_stored: u64 = index.entries.values().map(|e| e.size_stored).sum();
            let files = index.entries.len();
            let savings = if total_original > 0 {
                (1.0 - (total_stored as f64 / total_original as f64)) * 100.0
            } else { 0.0 };
            
            println!("Files: {}", files);
            println!("Original size: {} bytes", total_original);
            println!("Stored size: {} bytes", total_stored);
            println!("Compression savings: {:.1}%", savings);
        }
    }
    
    Ok(())
}
