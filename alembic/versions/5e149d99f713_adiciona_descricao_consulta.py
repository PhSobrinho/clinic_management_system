"""adiciona upgrade a tabela consultas

Revision ID: 5e149d99f713
Create Date: 2026-10-05 00:41:36.054450
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "5e149d99f713"
down_revision = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "consultas",
        sa.Column("descricao_consulta", sa.String(length=200), nullable=False)
    )

    op.alter_column(
        "consultas",
        "data_hora",
        existing_type=mysql.DATETIME(),
        type_=mysql.TIMESTAMP(),
        existing_nullable=False
    )

    op.alter_column(
        "consultas",
        "status",
        existing_type=mysql.VARCHAR(length=20),
        nullable=False
    )

    op.create_index(
        "idx_dentista_data",
        "consultas",
        ["dentista_id", "data_hora"],
        unique=False
    )

    op.create_index(
        "ix_consultas_data_hora",
        "consultas",
        ["data_hora"],
        unique=False
    )

    op.create_index(
        "ix_consultas_dentista_id",
        "consultas",
        ["dentista_id"],
        unique=False
    )

    op.create_index(
        "ix_consultas_paciente_id",
        "consultas",
        ["paciente_id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_consultas_paciente_id",
        table_name="consultas"
    )

    op.drop_index(
        "ix_consultas_dentista_id",
        table_name="consultas"
    )

    op.drop_index(
        "ix_consultas_data_hora",
        table_name="consultas"
    )

    op.drop_index(
        "idx_dentista_data",
        table_name="consultas"
    )

    op.alter_column(
        "consultas",
        "status",
        existing_type=mysql.VARCHAR(length=20),
        nullable=True
    )

    op.alter_column(
        "consultas",
        "data_hora",
        existing_type=mysql.TIMESTAMP(),
        type_=mysql.DATETIME(),
        existing_nullable=False
    )

    op.drop_column(
        "consultas",
        "descricao_consulta"
    )