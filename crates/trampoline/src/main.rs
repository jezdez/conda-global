//! Trampoline binary for conda-global.
//!
//! A minimal binary that reads a JSON configuration file, sets up
//! environment variables, and launches the real tool binary. Each
//! globally installed tool gets a hardlink to this single binary;
//! the trampoline determines which tool to launch based on its own
//! filename.
//!
//! Clean-room implementation inspired by pixi's trampoline design
//! (BSD-3-Clause). No code is shared.

use fs_err::File;
use serde::Deserialize;
use std::collections::HashMap;
use std::env;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

const TRAMPOLINE_CONFIGURATION: &str = ".trampoline";

#[derive(Deserialize, Debug)]
struct Configuration {
    /// Path to the original binary.
    exe: PathBuf,
    /// Paths to prepend to PATH.
    path_diff: String,
    /// Environment variables to set before launching.
    env: HashMap<String, String>,
}

fn read_configuration(current_exe: &Path) -> Result<Configuration, Box<dyn std::error::Error>> {
    let exe_parent = current_exe
        .parent()
        .ok_or("cannot determine parent directory of trampoline")?;

    let exe_name = executable_name(current_exe);
    let config_path = exe_parent
        .join(TRAMPOLINE_CONFIGURATION)
        .join(format!("{exe_name}.json"));

    let file = File::open(&config_path)
        .map(std::io::BufReader::new)
        .map_err(|e| format!("cannot open config {}: {e}", config_path.display()))?;

    let config: Configuration = serde_json::from_reader(file)
        .map_err(|e| format!("cannot parse config {}: {e}", config_path.display()))?;

    Ok(config)
}

/// Extract the tool name from the trampoline's own binary path,
/// stripping platform-specific extensions.
fn executable_name(path: &Path) -> String {
    let name = path
        .file_name()
        .unwrap_or(path.as_os_str())
        .to_string_lossy()
        .to_string();

    if cfg!(target_family = "windows") {
        strip_windows_extension(name)
    } else {
        name
    }
}

/// Strip Windows binary extensions using PATHEXT.
fn strip_windows_extension(name: String) -> String {
    let lowercase = name.to_lowercase();
    let extensions: Vec<String> = if let Ok(pathext) = env::var("PATHEXT") {
        pathext.split(';').map(|s| s.to_lowercase()).collect()
    } else {
        vec![
            ".com", ".exe", ".bat", ".cmd", ".vbs", ".vbe", ".js", ".jse",
            ".wsf", ".wsh", ".msc", ".cpl",
        ]
        .into_iter()
        .map(String::from)
        .collect()
    };

    for ext in extensions {
        if lowercase.ends_with(&ext) {
            return name[..name.len() - ext.len()].to_string();
        }
    }
    name
}

/// Compute the new PATH by prepending path_diff entries.
fn setup_path(path_diff: &str) -> Result<String, Box<dyn std::error::Error>> {
    let current_path = env::var("PATH").unwrap_or_default();
    let current_paths = env::split_paths(&current_path);
    let diff_paths = env::split_paths(path_diff);

    let paths: Vec<PathBuf> = diff_paths.chain(current_paths).collect();

    Ok(env::join_paths(paths)
        .map_err(|e| format!("cannot join PATH: {e}"))?
        .to_string_lossy()
        .to_string())
}

/// Replace this process with the target binary on Unix,
/// or spawn and wait on Windows.
fn launch_tool(config: &Configuration, args: &[String]) -> Result<(), Box<dyn std::error::Error>> {
    let mut cmd = Command::new(&config.exe);

    for (key, value) in &config.env {
        cmd.env(key, value);
    }

    cmd.env("PATH", setup_path(&config.path_diff)?);
    cmd.args(args);
    cmd.stdin(Stdio::inherit())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit());

    // On Unix: replace the trampoline process via execvp
    #[cfg(target_family = "unix")]
    {
        use std::os::unix::process::CommandExt;
        // Replace this process with the target via execvp
        let err = CommandExt::exec(&mut cmd);
        eprintln!("failed to launch {}: {err}", config.exe.display());
        std::process::exit(1);
    }

    // On Windows: spawn a child and forward exit code
    #[cfg(target_os = "windows")]
    {
        let mut child = cmd
            .spawn()
            .map_err(|e| format!("cannot spawn {}: {e}", config.exe.display()))?;

        let status = child
            .wait()
            .map_err(|e| format!("cannot wait for {}: {e}", config.exe.display()))?;

        std::process::exit(status.code().unwrap_or(1));
    }
}

fn trampoline() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    let current_exe = env::current_exe()
        .map_err(|e| format!("cannot determine current binary: {e}"))?;
    // Resolve symlinks (needed on macOS and Windows)
    let current_exe = current_exe.canonicalize().unwrap_or(current_exe);

    // Ignore Ctrl-C in the trampoline — let the child handle it
    ctrlc::set_handler(move || {})
        .map_err(|e| format!("cannot set signal handler: {e}"))?;

    let config = read_configuration(&current_exe)?;
    launch_tool(&config, &args[1..])?;

    Ok(())
}

fn main() {
    if let Err(err) = trampoline() {
        eprintln!("conda-global trampoline error: {err}");
        std::process::exit(1);
    }
}
