from alembic import context
from backend.models import Base, engine
config=context.config
target_metadata=Base.metadata
def run(connection):
    context.configure(connection=connection,target_metadata=target_metadata,compare_type=True,render_as_batch=connection.dialect.name=='sqlite')
    with context.begin_transaction():context.run_migrations()
if context.is_offline_mode():
    context.configure(url=str(engine.url),target_metadata=target_metadata,literal_binds=True,dialect_opts={'paramstyle':'named'})
    with context.begin_transaction():context.run_migrations()
else:
    connection=config.attributes.get('connection')
    if connection is not None:run(connection)
    else:
        with engine.connect() as connection:run(connection)
