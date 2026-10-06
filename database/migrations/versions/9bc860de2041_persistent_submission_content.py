"""Persist private uploaded content for serverless deployment."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGBLOB
revision='9bc860de2041'
down_revision='7a9990df7af4'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('submission_content',
        sa.Column('submission_id',sa.Integer(),nullable=False),
        sa.Column('content',sa.LargeBinary().with_variant(LONGBLOB(),'mysql'),nullable=False),
        sa.ForeignKeyConstraint(['submission_id'],['submissions.id'],ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('submission_id'))
def downgrade():op.drop_table('submission_content')
