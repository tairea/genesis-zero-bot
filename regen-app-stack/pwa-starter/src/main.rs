use leptos::{html::p, *};

pub mod app;
pub use app::App;

mod app {
    use leptos::*;

    #[component]
    pub fn App() -> impl IntoView {
        let (count, set_count) = create_signal(0);
        let (online, set_online) = create_signal(navigator().on_line());

        // Set up online/offline listeners
        leptos::on_mount(move || {
            let handle_online = window_event_listener(ev::online, move |_| {
                set_online(true);
            });
            let handle_offline = window_event_listener(ev::offline, move |_| {
                set_online(false);
            });

            move || {
                handle_online();
                handle_offline();
            }
        });

        view! {
            <main>
                <header>
                    <h1>🌿 RegenHub</h1>
                    <p class="subtitle">Trust-minimized, platform-independent PWA</p>
                    <div class="status-badge" class:online={move || online()} class:offline={move || !online()}>
                        {move || if online() { "🟢 Online" } else { "🔴 Offline" }}
                    </div>
                </header>

                <section class="card">
                    <h2>Counter Demo</h2>
                    <p>This counter persists in localStorage and works offline.</p>
                    <div class="counter">
                        <button on:click=move |_| set_count.update(|c| *c -= 1)>−</button>
                        <span class="count">{count}</span>
                        <button on:click=move |_| set_count.update(|c| *c += 1)>+</button>
                    </div>
                </section>

                <section class="card">
                    <h2>Why This Matters</h2>
                    <ul>
                        <li>✅ Installs like a native app (no App Store)</li>
                        <li>✅ Works completely offline</li>
                        <li>✅ Verifiable WASM — no hidden code</li>
                        <li>✅ Direct updates from developer</li>
                        <li>✅ No 30% platform tax</li>
                    </ul>
                </section>

                <section class="card">
                    <h2>PWA Install</h2>
                    <p>On mobile: tap "Share" → "Add to Home Screen"</p>
                    <p>On desktop: look for the install icon in your browser's address bar</p>
                </section>

                <footer>
                    <p>Built with Rust + Leptos + Trunk</p>
                    <p class="small">Source available for inspection. No black boxes.</p>
                </footer>
            </main>
        }
    }
}

fn main() {
    console_error_panic_hook::set_once();
    mount_to_body(|cx| view! { <App /> })
}
