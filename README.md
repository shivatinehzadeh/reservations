# reservations

This project is a reservation management system built with FastAPI, SQLAlchemy, and PostgreSQL. It allows users to create reservations and guest information, and log events to Kafka for auditing purposes.

Key features include:

Reservation Handling: Create, validate, and store reservations with guest associations.

Guest Management: Prevent duplicate guests using unique email constraints.

Event Logging: Audit reservation events to Kafka and log them in the database.

Robust Error Handling: Handles validation errors, database integrity errors, and internal server errors with proper HTTP responses.

Testing Strategy: Includes unit tests with mocked database sessions and Kafka producers, as well as integration tests with a real test database.

Logging: Detailed logs written to both console and files for easy monitoring.