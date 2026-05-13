use serde_json::Value;

/// Extract a string field from a JSON args object.
pub(super) fn string_arg(args: &Value, name: &str) -> Option<String> {
    args.get(name).and_then(|v| v.as_str()).map(String::from)
}

/// Extract an optional i64 field; error if the field is present but not an integer.
pub(super) fn i64_arg(args: &Value, name: &str) -> anyhow::Result<Option<i64>> {
    let Some(v) = args.get(name) else {
        return Ok(None);
    };
    v.as_i64()
        .map(Some)
        .ok_or_else(|| anyhow::anyhow!("\"{name}\" must be an integer, got {v:?}"))
}

/// Extract an optional usize field (clamped to 0–10_000).
pub(super) fn usize_arg(args: &Value, name: &str) -> anyhow::Result<Option<usize>> {
    i64_arg(args, name).map(|opt| opt.map(|n| n.clamp(0, 10_000) as usize))
}
