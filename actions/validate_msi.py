from core.action import InstallerAction
import logging
import os
import struct

logger = logging.getLogger("installer.actions.validate_msi")

class ValidateMSIAction(InstallerAction):
    name = 'validate_msi'

    # MSI file magic number (Compound File Binary Format / OLE2)
    MSI_MAGIC = b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'

    def do(self, state):
        """Validate the built MSI installer and optionally the CAB file"""
        msi_path = getattr(state.library, 'msi_path', None)
        cab_path = getattr(state.library, 'cab_path', None)

        validation_passed = True
        errors = []

        # Validate MSI file
        if msi_path:
            msi_valid, msi_errors = self._validate_msi_file(msi_path)
            if not msi_valid:
                validation_passed = False
                errors.extend(msi_errors)
            else:
                logging.info(f"MSI validation passed: {msi_path}")
        else:
            logging.warning("No MSI path found in state - skipping MSI validation")

        # Validate CAB file if present
        if cab_path:
            cab_valid, cab_errors = self._validate_cab_file(cab_path)
            if not cab_valid:
                validation_passed = False
                errors.extend(cab_errors)
            else:
                logging.info(f"CAB validation passed: {cab_path}")

        # Store validation result in state
        state.library.validation_passed = validation_passed
        state.library.validation_errors = errors

        if validation_passed:
            logging.info("All installer validation checks passed")
        else:
            for error in errors:
                logging.error(f"Validation error: {error}")
            logging.error(f"Installer validation failed with {len(errors)} error(s)")

    def _validate_msi_file(self, msi_path):
        """Validate an MSI file"""
        errors = []

        # Check file exists
        if not os.path.exists(msi_path):
            return False, [f"MSI file does not exist: {msi_path}"]

        # Check file is not empty
        file_size = os.path.getsize(msi_path)
        if file_size == 0:
            return False, [f"MSI file is empty: {msi_path}"]

        # Check minimum reasonable size for an MSI (at least 1KB)
        if file_size < 1024:
            errors.append(f"MSI file suspiciously small ({file_size} bytes): {msi_path}")

        # Validate MSI magic number (OLE2 Compound Document)
        try:
            with open(msi_path, 'rb') as f:
                magic = f.read(8)
                if magic != self.MSI_MAGIC:
                    return False, [f"Invalid MSI file format - bad magic number: {msi_path}"]
        except IOError as e:
            return False, [f"Cannot read MSI file: {e}"]

        # Try to open with msilib for deeper validation
        try:
            import msilib
            db = msilib.OpenDatabase(msi_path, msilib.MSIDBOPEN_READONLY)

            # Verify essential tables exist
            essential_tables = ['Property', 'File', 'Component', 'Feature', 'Directory']
            for table in essential_tables:
                try:
                    view = db.OpenView(f"SELECT * FROM `{table}`")
                    view.Execute(None)
                    view.Close()
                except Exception:
                    errors.append(f"MSI missing or invalid table: {table}")

            # Get and log some basic info
            try:
                view = db.OpenView("SELECT `Value` FROM `Property` WHERE `Property` = 'ProductName'")
                view.Execute(None)
                record = view.Fetch()
                if record:
                    product_name = record.GetString(1)
                    logging.info(f"MSI Product Name: {product_name}")
                view.Close()
            except Exception:
                pass  # Non-critical

            db.Close()

        except ImportError:
            logging.warning("msilib not available - skipping deep MSI validation")
        except Exception as e:
            errors.append(f"MSI structure validation failed: {e}")

        return len(errors) == 0, errors

    def _validate_cab_file(self, cab_path):
        """Validate a CAB (cabinet) file"""
        errors = []

        # Check file exists
        if not os.path.exists(cab_path):
            return False, [f"CAB file does not exist: {cab_path}"]

        # Check file is not empty
        file_size = os.path.getsize(cab_path)
        if file_size == 0:
            return False, [f"CAB file is empty: {cab_path}"]

        # Validate CAB magic number
        CAB_MAGIC = b'MSCF'  # Microsoft Cabinet File
        try:
            with open(cab_path, 'rb') as f:
                magic = f.read(4)
                if magic != CAB_MAGIC:
                    return False, [f"Invalid CAB file format - bad magic number: {cab_path}"]

                # Read CAB header to validate structure
                f.seek(0)
                header = f.read(36)  # Minimum CAB header size
                if len(header) < 36:
                    return False, [f"CAB file too small for valid header: {cab_path}"]

                # Parse cabinet size from header (bytes 8-11, little-endian)
                cabinet_size = struct.unpack('<I', header[8:12])[0]
                if cabinet_size != file_size:
                    errors.append(f"CAB header size ({cabinet_size}) doesn't match file size ({file_size})")

                # Parse file count (bytes 26-27, little-endian)
                file_count = struct.unpack('<H', header[26:28])[0]
                logging.info(f"CAB contains {file_count} file(s)")

        except IOError as e:
            return False, [f"Cannot read CAB file: {e}"]
        except struct.error as e:
            return False, [f"CAB header parsing error: {e}"]

        return len(errors) == 0, errors
