fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("proto/inference.proto")?;
    println!("cargo:rerun-if-changed=proto/inference.proto");
    Ok(())
}
