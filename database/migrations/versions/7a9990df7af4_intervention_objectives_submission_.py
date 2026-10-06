"""Add intervention and review metadata, preserving legacy unknown values."""
from alembic import op
import sqlalchemy as sa
revision='7a9990df7af4'
down_revision='0d98487f8ec7'
branch_labels=None
depends_on=None

def upgrade():
    # MySQL DDL commits independently: permit resuming a partially applied revision.
    existing={c['name'] for c in sa.inspect(op.get_bind()).get_columns('assignments')}
    if 'student_id' not in existing:
        with op.batch_alter_table('assignments') as batch:
            batch.add_column(sa.Column('student_id',sa.Integer(),nullable=True))
            batch.add_column(sa.Column('created_at',sa.String(40),nullable=True))
            batch.create_index('ix_assignments_student_id',['student_id'])
            batch.create_foreign_key('fk_assignments_student_id','students',['student_id'],['id'])
    existing={c['name'] for c in sa.inspect(op.get_bind()).get_columns('extra_classes')}
    if 'objective' not in existing:
        with op.batch_alter_table('extra_classes') as batch:
            batch.add_column(sa.Column('objective',sa.Text(),nullable=True))
            batch.add_column(sa.Column('created_by',sa.Integer(),nullable=True))
            batch.add_column(sa.Column('created_at',sa.String(40),nullable=True))
            batch.add_column(sa.Column('updated_at',sa.String(40),nullable=True))
            batch.create_foreign_key('fk_extra_classes_created_by','users',['created_by'],['id'])
    op.execute(sa.text("UPDATE extra_classes SET objective='' WHERE objective IS NULL"))
    with op.batch_alter_table('extra_classes') as batch:
        batch.alter_column('objective',existing_type=sa.Text(),nullable=False)
    existing={c['name'] for c in sa.inspect(op.get_bind()).get_columns('submissions')}
    if 'file_hash' not in existing:
        with op.batch_alter_table('submissions') as batch:
            batch.add_column(sa.Column('file_hash',sa.String(64),nullable=True))
            batch.add_column(sa.Column('marks',sa.Float(),nullable=True))
            batch.add_column(sa.Column('reviewed_by',sa.Integer(),nullable=True))
            batch.add_column(sa.Column('reviewed_at',sa.String(40),nullable=True))
            batch.create_foreign_key('fk_submissions_reviewed_by','users',['reviewed_by'],['id'])

def downgrade():
    with op.batch_alter_table('submissions') as batch:
        batch.drop_constraint('fk_submissions_reviewed_by',type_='foreignkey')
        for column in ('reviewed_at','reviewed_by','marks','file_hash'):batch.drop_column(column)
    with op.batch_alter_table('extra_classes') as batch:
        batch.drop_constraint('fk_extra_classes_created_by',type_='foreignkey')
        for column in ('updated_at','created_at','created_by','objective'):batch.drop_column(column)
    with op.batch_alter_table('assignments') as batch:
        batch.drop_constraint('fk_assignments_student_id',type_='foreignkey')
        batch.drop_index('ix_assignments_student_id')
        batch.drop_column('created_at');batch.drop_column('student_id')
