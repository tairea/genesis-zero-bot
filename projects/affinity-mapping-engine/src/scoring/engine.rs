use chrono::Utc;
use uuid::Uuid;

use crate::models::{
    AffinityCluster, AffinityLayer, LayerKind, Member, RelationshipScore, SemanticNode,
};

/// Core scoring engine for computing affinity relationships
pub struct ScoringEngine {
    /// Weight multipliers per layer kind
    pub layer_weights: LayerWeights,
    /// Minimum score to consider a relationship meaningful
    pub min_relationship_threshold: f64,
    /// Minimum cohesion for cluster formation
    pub min_cluster_cohesion: f64,
}

pub struct LayerWeights {
    pub needs: f64,
    pub beliefs: f64,
    pub principles: f64,
    pub values: f64,
}

impl Default for LayerWeights {
    fn default() -> Self {
        Self {
            needs: 1.0,
            beliefs: 1.5,
            principles: 2.0,
            values: 2.5,
        }
    }
}

impl LayerWeights {
    pub fn get(&self, kind: LayerKind) -> f64 {
        match kind {
            LayerKind::Needs => self.needs,
            LayerKind::Beliefs => self.beliefs,
            LayerKind::Principles => self.principles,
            LayerKind::Values => self.values,
        }
    }
}

/// Compute label overlap similarity between two sets of semantic nodes.
/// Uses Jaccard-like coefficient on normalized labels, weighted by node weights.
fn layer_similarity(a: &AffinityLayer, b: &AffinityLayer) -> f64 {
    if a.nodes.is_empty() && b.nodes.is_empty() {
        return 0.0;
    }
    if a.nodes.is_empty() || b.nodes.is_empty() {
        return 0.0;
    }

    let mut weighted_overlap = 0.0;
    let mut total_possible = 0.0;

    for node_a in &a.nodes {
        let norm_a = node_a.label.to_lowercase();
        let mut best_match = 0.0_f64;
        for node_b in &b.nodes {
            let norm_b = node_b.label.to_lowercase();
            let sim = label_similarity(&norm_a, &norm_b);
            best_match = best_match.max(sim);
        }
        // Weight by the geometric mean of both node weights
        let pair_weight = node_a.weight;
        weighted_overlap += best_match * pair_weight;
        total_possible += pair_weight;
    }

    // Also check from B's perspective (symmetric)
    for node_b in &b.nodes {
        let norm_b = node_b.label.to_lowercase();
        let mut best_match = 0.0_f64;
        for node_a in &a.nodes {
            let norm_a = node_a.label.to_lowercase();
            let sim = label_similarity(&norm_b, &norm_a);
            best_match = best_match.max(sim);
        }
        let pair_weight = node_b.weight;
        weighted_overlap += best_match * pair_weight;
        total_possible += pair_weight;
    }

    if total_possible == 0.0 {
        0.0
    } else {
        (weighted_overlap / total_possible).clamp(0.0, 1.0)
    }
}

/// Similarity between two labels: exact match = 1.0, word overlap otherwise.
fn label_similarity(a: &str, b: &str) -> f64 {
    if a == b {
        return 1.0;
    }

    let words_a: std::collections::HashSet<&str> = a.split_whitespace().collect();
    let words_b: std::collections::HashSet<&str> = b.split_whitespace().collect();

    let intersection = words_a.intersection(&words_b).count() as f64;
    let union = words_a.union(&words_b).count() as f64;

    if union == 0.0 {
        0.0
    } else {
        intersection / union
    }
}

impl ScoringEngine {
    pub fn new() -> Self {
        Self {
            layer_weights: LayerWeights::default(),
            min_relationship_threshold: 0.05,
            min_cluster_cohesion: 0.3,
        }
    }

    pub fn with_weights(layer_weights: LayerWeights) -> Self {
        Self {
            layer_weights,
            min_relationship_threshold: 0.05,
            min_cluster_cohesion: 0.3,
        }
    }

    /// Compute relationship score between two members for a given layer.
    /// Returns a RelationshipScore with strength in [0.0, 1.0] after applying layer weight.
    pub fn compute_layer_score(
        &self,
        member_a: &Member,
        member_b: &Member,
        layer: LayerKind,
    ) -> RelationshipScore {
        let (layer_a, layer_b) = match layer {
            LayerKind::Needs => (&member_a.seed_profile.needs, &member_b.seed_profile.needs),
            LayerKind::Beliefs => {
                (&member_a.seed_profile.beliefs, &member_b.seed_profile.beliefs)
            }
            LayerKind::Principles => (
                &member_a.seed_profile.principles,
                &member_b.seed_profile.principles,
            ),
            LayerKind::Values => (&member_a.seed_profile.values, &member_b.seed_profile.values),
        };

        let strength = layer_similarity(layer_a, layer_b);

        RelationshipScore {
            member_a: member_a.id,
            member_b: member_b.id,
            layer,
            strength,
            last_updated: Utc::now(),
            locked_until: None,
        }
    }

    /// Compute the composite affinity score across all four layers.
    /// Returns a vec of per-layer scores plus a summary composite score.
    pub fn compute_composite_score(
        &self,
        member_a: &Member,
        member_b: &Member,
    ) -> CompositeScore {
        let layers = [
            LayerKind::Needs,
            LayerKind::Beliefs,
            LayerKind::Principles,
            LayerKind::Values,
        ];

        let mut layer_scores = Vec::with_capacity(4);
        let mut weighted_sum = 0.0;
        let mut weight_total = 0.0;

        for layer in &layers {
            let score = self.compute_layer_score(member_a, member_b, *layer);
            let weight = self.layer_weights.get(*layer);
            weighted_sum += score.strength * weight;
            weight_total += weight;
            layer_scores.push(score);
        }

        let composite = if weight_total > 0.0 {
            weighted_sum / weight_total
        } else {
            0.0
        };

        CompositeScore {
            member_a: member_a.id,
            member_b: member_b.id,
            layer_scores,
            composite,
        }
    }

    /// Update a semantic node's weight based on interaction frequency.
    /// Weight grows with repeated interactions but is capped at 1.0.
    pub fn reinforce_node(node: &mut SemanticNode, interaction_strength: f64) {
        let delta = interaction_strength * (1.0 - node.weight);
        node.weight = (node.weight + delta).clamp(0.0, 1.0);
    }

    /// Discover affinity clusters from a set of relationship scores.
    /// Uses a simple greedy agglomerative approach:
    /// members with mutual scores above threshold get grouped together.
    pub fn discover_clusters(
        &self,
        scores: &[RelationshipScore],
    ) -> Vec<AffinityCluster> {
        // Build adjacency: only consider scores above threshold
        let mut adjacency: std::collections::HashMap<Uuid, std::collections::HashSet<Uuid>> =
            std::collections::HashMap::new();

        for score in scores {
            if score.strength >= self.min_relationship_threshold {
                adjacency
                    .entry(score.member_a)
                    .or_default()
                    .insert(score.member_b);
                adjacency
                    .entry(score.member_b)
                    .or_default()
                    .insert(score.member_a);
            }
        }

        // Connected components via BFS
        let mut visited: std::collections::HashSet<Uuid> = std::collections::HashSet::new();
        let mut clusters = Vec::new();

        for &start in adjacency.keys() {
            if visited.contains(&start) {
                continue;
            }

            let mut component = Vec::new();
            let mut queue = std::collections::VecDeque::new();
            queue.push_back(start);
            visited.insert(start);

            while let Some(current) = queue.pop_front() {
                component.push(current);
                if let Some(neighbors) = adjacency.get(&current) {
                    for &neighbor in neighbors {
                        if visited.insert(neighbor) {
                            queue.push_back(neighbor);
                        }
                    }
                }
            }

            // Compute cluster cohesion: average score among members in the cluster
            let mut score_sum = 0.0;
            let mut score_count = 0;
            let member_set: std::collections::HashSet<Uuid> =
                component.iter().copied().collect();

            for score in scores {
                if member_set.contains(&score.member_a) && member_set.contains(&score.member_b) {
                    score_sum += score.strength;
                    score_count += 1;
                }
            }

            let cohesion = if score_count > 0 {
                score_sum / score_count as f64
            } else {
                0.0
            };

            // Only form clusters with sufficient cohesion and at least 2 members
            if component.len() >= 2 && cohesion >= self.min_cluster_cohesion {
                // Centroid scores: average strength per layer
                let mut layer_sums = std::collections::HashMap::new();
                let mut layer_counts = std::collections::HashMap::new();
                for score in scores {
                    if member_set.contains(&score.member_a)
                        && member_set.contains(&score.member_b)
                    {
                        *layer_sums.entry(score.layer).or_insert(0.0) += score.strength;
                        *layer_counts.entry(score.layer).or_insert(0u32) += 1;
                    }
                }

                let centroid_scores: Vec<f64> = [
                    LayerKind::Needs,
                    LayerKind::Beliefs,
                    LayerKind::Principles,
                    LayerKind::Values,
                ]
                .iter()
                .map(|kind| {
                    let sum = layer_sums.get(kind).copied().unwrap_or(0.0);
                    let count = layer_counts.get(kind).copied().unwrap_or(0);
                    if count > 0 {
                        sum / count as f64
                    } else {
                        0.0
                    }
                })
                .collect();

                clusters.push(AffinityCluster {
                    id: Uuid::new_v4(),
                    members: component,
                    centroid_scores,
                    cohesion,
                });
            }
        }

        clusters
    }

}

impl Default for ScoringEngine {
    fn default() -> Self {
        Self::new()
    }
}

/// Composite score combining all four layer scores
#[derive(Debug, Clone)]
pub struct CompositeScore {
    pub member_a: Uuid,
    pub member_b: Uuid,
    pub layer_scores: Vec<RelationshipScore>,
    pub composite: f64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::seed::{create_member, CreateMemberRequest};

    fn alice() -> Member {
        create_member(&CreateMemberRequest {
            name: "Alice".into(),
            needs: vec!["shelter".into(), "community".into(), "food".into()],
            beliefs: vec!["mutual aid".into(), "solidarity".into()],
            principles: vec!["consent".into(), "autonomy".into()],
            values: vec!["regeneration".into(), "care".into()],
        })
        .unwrap()
    }

    fn bob_similar() -> Member {
        create_member(&CreateMemberRequest {
            name: "Bob".into(),
            needs: vec!["shelter".into(), "community".into()],
            beliefs: vec!["mutual aid".into()],
            principles: vec!["consent".into(), "transparency".into()],
            values: vec!["regeneration".into(), "justice".into()],
        })
        .unwrap()
    }

    fn charlie_different() -> Member {
        create_member(&CreateMemberRequest {
            name: "Charlie".into(),
            needs: vec!["profit".into(), "growth".into()],
            beliefs: vec!["competition".into()],
            principles: vec!["hierarchy".into()],
            values: vec!["efficiency".into()],
        })
        .unwrap()
    }

    fn empty_member() -> Member {
        create_member(&CreateMemberRequest {
            name: "Empty".into(),
            needs: vec![],
            beliefs: vec![],
            principles: vec![],
            values: vec![],
        })
        .unwrap()
    }

    #[test]
    fn identical_labels_score_high() {
        let engine = ScoringEngine::new();
        let a = alice();
        // Score alice against herself-like member
        let b = create_member(&CreateMemberRequest {
            name: "Alice Clone".into(),
            needs: vec!["shelter".into(), "community".into(), "food".into()],
            beliefs: vec!["mutual aid".into(), "solidarity".into()],
            principles: vec!["consent".into(), "autonomy".into()],
            values: vec!["regeneration".into(), "care".into()],
        })
        .unwrap();
        let composite = engine.compute_composite_score(&a, &b);
        // Identical labels should produce high composite score
        assert!(
            composite.composite > 0.8,
            "identical labels should score high, got {}",
            composite.composite
        );
    }

    #[test]
    fn no_overlap_scores_zero() {
        let engine = ScoringEngine::new();
        let a = alice();
        let c = charlie_different();
        let composite = engine.compute_composite_score(&a, &c);
        assert!(
            composite.composite < 0.01,
            "no overlap should score near zero, got {}",
            composite.composite
        );
    }

    #[test]
    fn partial_overlap_scores_middle() {
        let engine = ScoringEngine::new();
        let a = alice();
        let b = bob_similar();
        let composite = engine.compute_composite_score(&a, &b);
        assert!(
            composite.composite > 0.1 && composite.composite < 0.9,
            "partial overlap should score in middle range, got {}",
            composite.composite
        );
    }

    #[test]
    fn empty_members_score_zero() {
        let engine = ScoringEngine::new();
        let e1 = empty_member();
        let e2 = empty_member();
        let composite = engine.compute_composite_score(&e1, &e2);
        assert_eq!(composite.composite, 0.0);
    }

    #[test]
    fn one_empty_member_scores_zero() {
        let engine = ScoringEngine::new();
        let a = alice();
        let e = empty_member();
        let composite = engine.compute_composite_score(&a, &e);
        assert_eq!(composite.composite, 0.0);
    }

    #[test]
    fn values_weighted_contribution_higher_than_needs() {
        let engine = ScoringEngine::new();
        // Create two members that share one value and one need equally
        let m1 = create_member(&CreateMemberRequest {
            name: "M1".into(),
            needs: vec!["shelter".into()],
            beliefs: vec![],
            principles: vec![],
            values: vec!["regeneration".into()],
        })
        .unwrap();
        let m2 = create_member(&CreateMemberRequest {
            name: "M2".into(),
            needs: vec!["shelter".into()],
            beliefs: vec![],
            principles: vec![],
            values: vec!["regeneration".into()],
        })
        .unwrap();

        let composite = engine.compute_composite_score(&m1, &m2);
        // Both layers have equal raw similarity, but values weight (2.5) > needs weight (1.0)
        // So values contributes more to the composite
        let values_score = composite
            .layer_scores
            .iter()
            .find(|s| s.layer == LayerKind::Values)
            .unwrap();
        let needs_score = composite
            .layer_scores
            .iter()
            .find(|s| s.layer == LayerKind::Needs)
            .unwrap();
        let values_contribution =
            values_score.strength * engine.layer_weights.get(LayerKind::Values);
        let needs_contribution =
            needs_score.strength * engine.layer_weights.get(LayerKind::Needs);
        assert!(
            values_contribution > needs_contribution,
            "values contribution ({}) should exceed needs contribution ({})",
            values_contribution,
            needs_contribution
        );
    }

    #[test]
    fn layer_score_bounded_zero_to_one() {
        let engine = ScoringEngine::new();
        let a = alice();
        let b = bob_similar();
        for layer in [
            LayerKind::Needs,
            LayerKind::Beliefs,
            LayerKind::Principles,
            LayerKind::Values,
        ] {
            let score = engine.compute_layer_score(&a, &b, layer);
            assert!(
                score.strength >= 0.0 && score.strength <= 1.0,
                "score for {:?} out of bounds: {}",
                layer,
                score.strength
            );
        }
    }

    #[test]
    fn reinforce_node_increases_weight() {
        let mut node = SemanticNode {
            id: Uuid::new_v4(),
            label: "test".into(),
            weight: 0.1,
            created_at: Utc::now(),
        };
        ScoringEngine::reinforce_node(&mut node, 0.5);
        assert!(node.weight > 0.1, "weight should increase");
        assert!(node.weight <= 1.0, "weight should not exceed 1.0");
    }

    #[test]
    fn reinforce_node_approaches_but_never_exceeds_one() {
        let mut node = SemanticNode {
            id: Uuid::new_v4(),
            label: "test".into(),
            weight: 0.9,
            created_at: Utc::now(),
        };
        for _ in 0..100 {
            ScoringEngine::reinforce_node(&mut node, 1.0);
        }
        assert!(node.weight <= 1.0);
        assert!(node.weight > 0.99);
    }

    #[test]
    fn reinforce_with_zero_strength_no_change() {
        let mut node = SemanticNode {
            id: Uuid::new_v4(),
            label: "test".into(),
            weight: 0.5,
            created_at: Utc::now(),
        };
        ScoringEngine::reinforce_node(&mut node, 0.0);
        assert!((node.weight - 0.5).abs() < f64::EPSILON);
    }

    #[test]
    fn discover_clusters_groups_connected_members() {
        let engine = ScoringEngine::new();
        let a = alice();
        let b = bob_similar();
        let c = charlie_different();

        // High score between a and b, low between a/b and c
        let scores = vec![
            RelationshipScore {
                member_a: a.id,
                member_b: b.id,
                layer: LayerKind::Values,
                strength: 0.8,
                last_updated: Utc::now(),
                locked_until: None,
            },
            RelationshipScore {
                member_a: a.id,
                member_b: c.id,
                layer: LayerKind::Values,
                strength: 0.01,
                last_updated: Utc::now(),
                locked_until: None,
            },
        ];

        let clusters = engine.discover_clusters(&scores);
        // a and b should be in a cluster, c should not
        assert!(!clusters.is_empty(), "should find at least one cluster");
        let ab_cluster = clusters
            .iter()
            .find(|cl| cl.members.contains(&a.id) && cl.members.contains(&b.id));
        assert!(ab_cluster.is_some(), "Alice and Bob should be clustered");
        let c_in_any = clusters.iter().any(|cl| cl.members.contains(&c.id));
        assert!(!c_in_any, "Charlie should not be in any cluster");
    }

    #[test]
    fn discover_clusters_empty_scores() {
        let engine = ScoringEngine::new();
        let clusters = engine.discover_clusters(&[]);
        assert!(clusters.is_empty());
    }

    #[test]
    fn discover_clusters_all_below_threshold() {
        let engine = ScoringEngine::new();
        let id_a = Uuid::new_v4();
        let id_b = Uuid::new_v4();
        let scores = vec![RelationshipScore {
            member_a: id_a,
            member_b: id_b,
            layer: LayerKind::Needs,
            strength: 0.01,
            last_updated: Utc::now(),
            locked_until: None,
        }];
        let clusters = engine.discover_clusters(&scores);
        assert!(clusters.is_empty());
    }

    #[test]
    fn cluster_cohesion_is_average_of_member_scores() {
        let engine = ScoringEngine {
            min_relationship_threshold: 0.05,
            min_cluster_cohesion: 0.0, // lower for this test
            ..ScoringEngine::new()
        };

        let id_a = Uuid::new_v4();
        let id_b = Uuid::new_v4();
        let id_c = Uuid::new_v4();

        let scores = vec![
            RelationshipScore {
                member_a: id_a,
                member_b: id_b,
                layer: LayerKind::Values,
                strength: 0.6,
                last_updated: Utc::now(),
                locked_until: None,
            },
            RelationshipScore {
                member_a: id_b,
                member_b: id_c,
                layer: LayerKind::Values,
                strength: 0.4,
                last_updated: Utc::now(),
                locked_until: None,
            },
            RelationshipScore {
                member_a: id_a,
                member_b: id_c,
                layer: LayerKind::Values,
                strength: 0.2,
                last_updated: Utc::now(),
                locked_until: None,
            },
        ];

        let clusters = engine.discover_clusters(&scores);
        assert_eq!(clusters.len(), 1);
        let cluster = &clusters[0];
        let expected_cohesion = (0.6 + 0.4 + 0.2) / 3.0;
        assert!(
            (cluster.cohesion - expected_cohesion).abs() < 0.001,
            "cohesion should be {}, got {}",
            expected_cohesion,
            cluster.cohesion
        );
    }

    #[test]
    fn composite_score_is_weighted_average() {
        let engine = ScoringEngine::new();
        let a = alice();
        let a_clone = create_member(&CreateMemberRequest {
            name: "A2".into(),
            needs: vec!["shelter".into(), "community".into(), "food".into()],
            beliefs: vec!["mutual aid".into(), "solidarity".into()],
            principles: vec!["consent".into(), "autonomy".into()],
            values: vec!["regeneration".into(), "care".into()],
        })
        .unwrap();

        let composite = engine.compute_composite_score(&a, &a_clone);
        // Verify composite is a weighted average of layer scores
        let total_weight = 1.0 + 1.5 + 2.0 + 2.5;
        let expected = composite
            .layer_scores
            .iter()
            .map(|s| s.strength * engine.layer_weights.get(s.layer))
            .sum::<f64>()
            / total_weight;
        assert!(
            (composite.composite - expected).abs() < 0.001,
            "composite {} should equal weighted average {}",
            composite.composite,
            expected
        );
    }

    #[test]
    fn word_overlap_partial_match() {
        // "mutual aid" vs "mutual support" should have partial similarity
        let sim = label_similarity("mutual aid", "mutual support");
        assert!(
            sim > 0.0 && sim < 1.0,
            "partial word overlap should give partial score, got {}",
            sim
        );
    }

    #[test]
    fn custom_weights_affect_composite() {
        let engine_needs_heavy = ScoringEngine::with_weights(LayerWeights {
            needs: 10.0,
            beliefs: 0.1,
            principles: 0.1,
            values: 0.1,
        });
        let engine_values_heavy = ScoringEngine::with_weights(LayerWeights {
            needs: 0.1,
            beliefs: 0.1,
            principles: 0.1,
            values: 10.0,
        });

        // Members share needs but not values
        let m1 = create_member(&CreateMemberRequest {
            name: "M1".into(),
            needs: vec!["shelter".into()],
            beliefs: vec![],
            principles: vec![],
            values: vec!["care".into()],
        })
        .unwrap();
        let m2 = create_member(&CreateMemberRequest {
            name: "M2".into(),
            needs: vec!["shelter".into()],
            beliefs: vec![],
            principles: vec![],
            values: vec!["justice".into()],
        })
        .unwrap();

        let needs_composite = engine_needs_heavy.compute_composite_score(&m1, &m2).composite;
        let values_composite = engine_values_heavy.compute_composite_score(&m1, &m2).composite;
        assert!(
            needs_composite > values_composite,
            "needs-heavy engine ({}) should score higher than values-heavy ({}) for needs-matched pair",
            needs_composite,
            values_composite
        );
    }
}
