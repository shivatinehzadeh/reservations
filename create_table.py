# from models import AuditLog, Guests, Reservations
from setup.database import Base, engine
from setup.logger import get_logger

logger = get_logger("create_table", "create_table.log")

if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        logger.info(
            f"All tables created successfully!\
            Table names={list(Base.metadata.tables.keys())}"
        )

    except Exception as e:
        print(f"Error creating tables: {e}")
        logger.error(f"Error creating tables: {e}")
