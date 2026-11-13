# PAPER024501 periodic checkpoints

The Mac's user LaunchAgent starts the checkpoint script every 1200 seconds
(20 minutes), plus once when loaded. It does **not** invoke ChatGPT or consume
ChatGPT model turns. It stages only seed-summary JSON, progress JSON and CSV;
full per-round simulation trajectories stay in the local workdirs. Every
successful checkpoint creates a commit only if there are new completed files,
then retries pushing all pending commits to the reviewer branch.

The runner is restartable based on the presence of completed per-seed JSON.
After interruption, rerun launch_parameter_sweep.sh when no instance is
running. GitHub Actions are not used to execute the full simulation because
the current workflow cannot install Conda. No automatic hardware booking or
remote testbed experiments are attempted.

The LaunchAgent works while the computer is powered on and the user LaunchAgent
is running. A Mac that is powered off cannot execute or sync checkpoints; any
uncommitted results since the last checkpoint remain only on local storage.
