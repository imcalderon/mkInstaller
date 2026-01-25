from core.action import InstallerAction
import logging
import os
import subprocess
import shutil
import tempfile

logger = logging.getLogger("installer.actions.make_pfw")

class InstallerMakePFWAction(InstallerAction):
    """
    Creates a self-extracting executable using ModernArchive technology.

    The generated executable will:
    1. Extract the MSI and any additional files to a temporary directory
    2. Automatically run msiexec to install the MSI package
    3. Support silent installation mode
    """
    name = 'make_pfw'

    # Default path to ModernArchive executable - can be overridden via options
    DEFAULT_ARCHIVE_EXE = r'E:\proj\ModernArchive\build\Release\archive.exe'

    def do(self, state):
        output_dir = getattr(state.library.options, 'output_dir', os.path.abspath('out'))
        os.makedirs(output_dir, exist_ok=True)

        logging.info("Creating self-extracting archive using ModernArchive...")

        # Get MSI path
        msi_path = getattr(state.library, 'msi_path', None)

        if not msi_path or not os.path.exists(msi_path):
            logging.warning("No MSI file found to package into self-extracting archive")
            state.library.pfw_path = None
            return

        # Get ModernArchive executable path from options or use default
        archive_exe = getattr(state.library.options, 'archive_exe', self.DEFAULT_ARCHIVE_EXE)

        if not os.path.exists(archive_exe):
            logging.error(f"ModernArchive executable not found at: {archive_exe}")
            logging.info("Falling back to simple copy method")
            self._fallback_copy(state, msi_path, output_dir)
            return

        # Build self-extracting executable
        pfw_name = f"{state.library.project_name}_setup.exe"
        pfw_path = os.path.join(output_dir, pfw_name)
        msi_filename = os.path.basename(msi_path)

        # Get additional files to include (if any)
        additional_files = getattr(state.library, 'additional_pfw_files', [])

        # Build configuration options from state
        silent_install = getattr(state.library.options, 'silent_install', False)
        install_args = getattr(state.library.options, 'msi_install_args', f'/i {msi_filename}')
        if silent_install:
            install_args += ' /quiet /norestart'

        try:
            # Prepare files in a temporary directory to ensure proper paths
            with tempfile.TemporaryDirectory(prefix='pfw_build_') as temp_dir:
                # Copy MSI to temp directory
                temp_msi = os.path.join(temp_dir, msi_filename)
                shutil.copy2(msi_path, temp_msi)

                # Copy additional files if any
                files_to_archive = [temp_msi]
                for additional_file in additional_files:
                    if os.path.exists(additional_file):
                        dest = os.path.join(temp_dir, os.path.basename(additional_file))
                        shutil.copy2(additional_file, dest)
                        files_to_archive.append(dest)

                # Build the ModernArchive command
                # Usage: archive selfext <output.exe> [options] <files...>
                cmd = [
                    archive_exe,
                    'selfext',
                    pfw_path,
                    '--exec', 'msiexec',
                    '--args', install_args,
                ]

                if silent_install:
                    cmd.append('--silent')

                # Add all files to archive
                cmd.extend(files_to_archive)

                logging.info(f"Running ModernArchive: {' '.join(cmd)}")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=temp_dir
                )

                if result.returncode != 0:
                    logging.error(f"ModernArchive failed with code {result.returncode}")
                    logging.error(f"stdout: {result.stdout}")
                    logging.error(f"stderr: {result.stderr}")
                    self._fallback_copy(state, msi_path, output_dir)
                    return

                if os.path.exists(pfw_path):
                    state.library.pfw_path = pfw_path
                    pfw_size = os.path.getsize(pfw_path)
                    logging.info(f"Self-extracting archive created: {pfw_path} ({pfw_size:,} bytes)")
                else:
                    logging.error("ModernArchive completed but output file not found")
                    self._fallback_copy(state, msi_path, output_dir)

        except FileNotFoundError as e:
            logging.error(f"ModernArchive executable not found: {e}")
            self._fallback_copy(state, msi_path, output_dir)
        except subprocess.SubprocessError as e:
            logging.error(f"Failed to run ModernArchive: {e}")
            self._fallback_copy(state, msi_path, output_dir)
        except Exception as e:
            logging.error(f"Unexpected error creating self-extracting archive: {e}")
            self._fallback_copy(state, msi_path, output_dir)

    def _fallback_copy(self, state, msi_path, output_dir):
        """Fallback method when ModernArchive is not available - just copy the MSI"""
        logging.warning("Using fallback method: copying MSI without self-extracting wrapper")
        pfw_name = f"{state.library.project_name}_setup.msi"
        pfw_path = os.path.join(output_dir, pfw_name)
        try:
            shutil.copy2(msi_path, pfw_path)
            state.library.pfw_path = pfw_path
            logging.info(f"Fallback: MSI copied to: {pfw_path}")
        except Exception as e:
            logging.error(f"Fallback copy also failed: {e}")
            state.library.pfw_path = None
