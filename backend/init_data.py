from models import Pipeline, get_db
from datetime import datetime
import uuid


def init_sample_data():
    db = next(get_db())

    # Sample pipelines
    pipelines = [
        Pipeline(
            id=str(uuid.uuid4()),
            name="frontend-pipeline",
            status="unknown",
            last_build_time=datetime.utcnow()
        ),
        Pipeline(
            id=str(uuid.uuid4()),
            name="backend-pipeline",
            status="unknown",
            last_build_time=datetime.utcnow()
        ),
        Pipeline(
            id=str(uuid.uuid4()),
            name="deployment-pipeline",
            status="unknown",
            last_build_time=datetime.utcnow()
        )
    ]

    # Add pipelines to database
    for pipeline in pipelines:
        db.add(pipeline)

    db.commit()
    print("Sample data initialized successfully!")


if __name__ == "__main__":
    init_sample_data()
