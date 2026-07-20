from http import HTTPStatus
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from loguru import logger

from app.core.settings import settings
from app.modules.shared.presentation.exceptions import StandardException


async def init_security_keys() -> None:
    try:
        logger.info("Checking security keys...")

        keys_dir = Path("secrets/keys")
        if not keys_dir.exists():
            logger.info(f"Creating directory: {keys_dir}")
            keys_dir.mkdir(parents=True, exist_ok=True)

        signing_private = Path(settings.JWT_SIGNING_PRIVATE_KEY_PATH)
        signing_public = Path(settings.JWT_SIGNING_PUBLIC_KEY_PATH)
        encryption_private = Path(settings.JWT_ENCRYPTION_PRIVATE_KEY_PATH)
        encryption_public = Path(settings.JWT_ENCRYPTION_PUBLIC_KEY_PATH)

        if not signing_private.exists() or not signing_public.exists():
            logger.info("Signing keys not found. Generating...")
            _generate_signing_keys(signing_private, signing_public)
            logger.info("Signing keys generated successfully.")
        else:
            logger.info("Signing keys already exist.")

        if not encryption_private.exists() or not encryption_public.exists():
            logger.info("Encryption keys not found. Generating...")
            _generate_encryption_keys(encryption_private, encryption_public)
            logger.info("Encryption keys generated successfully.")
        else:
            logger.info("Encryption keys already exist.")

    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred while initializing security keys."
        )
        raise


def _generate_signing_keys(private_path: Path, public_path: Path) -> None:
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend(),
        )

        password = settings.JWT_SIGNING_KEY_PASSWORD.encode()

        with open(private_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(password),
                )
            )

        public_key = private_key.public_key()

        with open(public_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        logger.info(f"Signing keys saved to {private_path} and {public_path}")

    except Exception as e:
        logger.error(f"Failed to generate signing keys: {e}")
        raise StandardException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Failed to generate signing keys.",
        )


def _generate_encryption_keys(private_path: Path, public_path: Path) -> None:
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend(),
        )

        password = settings.JWT_ENCRYPTION_KEY_PASSWORD.encode()

        with open(private_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(password),
                )
            )

        public_key = private_key.public_key()

        with open(public_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        logger.info(f"Encryption keys saved to {private_path} and {public_path}")

    except Exception as e:
        logger.error(f"Failed to generate encryption keys: {e}")
        raise StandardException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Failed to generate encryption keys.",
        )
