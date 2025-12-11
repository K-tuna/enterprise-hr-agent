"""
Database Connection
MySQL 데이터베이스 연결 관리 (DI 친화적)
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

from core.types.errors import DatabaseConnectionError


class DatabaseConnection:
    """
    MySQL 데이터베이스 연결 관리 클래스

    사용법:
        db = DatabaseConnection(connection_url="mysql+pymysql://...")
        results, error = db.execute_query("SELECT * FROM employees")
    """

    def __init__(
        self,
        connection_url: str,
        pool_size: int = 5,
        pool_recycle: int = 3600,
    ):
        """
        Args:
            connection_url: SQLAlchemy 연결 URL
            pool_size: 커넥션 풀 크기
            pool_recycle: 커넥션 재활용 시간(초)
        """
        if not connection_url:
            raise DatabaseConnectionError("DATABASE_URL이 설정되지 않았습니다.")

        self.connection_url = connection_url

        # SQLAlchemy 엔진 생성
        self.engine: Engine = create_engine(
            connection_url,
            pool_pre_ping=True,
            pool_size=pool_size,
            pool_recycle=pool_recycle,
        )

        self.SessionLocal = sessionmaker(bind=self.engine)

    def test_connection(self) -> bool:
        """DB 연결 테스트"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            raise DatabaseConnectionError(f"DB 연결 실패: {e}")

    def execute_query(
        self, query: str
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        SQL 쿼리 실행 (SELECT 등)

        Args:
            query: 실행할 SQL 쿼리 문자열

        Returns:
            tuple: (결과 리스트, 에러 메시지)
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = result.keys()

                # 결과를 딕셔너리 리스트로 변환
                results = [dict(zip(columns, row)) for row in rows]

                return results, None
        except Exception as e:
            return None, str(e)

    def get_table_schema(self) -> str:
        """
        DB의 모든 테이블 및 컬럼 스키마를 문자열로 반환.
        Text-to-SQL 프롬프트에 필요.
        샘플 데이터도 포함 (코드성 테이블은 전체, 일반 테이블은 3개)
        """
        # 코드성 테이블 (전체 데이터 표시)
        CODE_TABLES = {"departments"}
        SAMPLE_LIMIT = 3

        try:
            # DB 이름 추출
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT DATABASE()"))
                db_name = result.fetchone()[0]

            if not db_name:
                return "스키마 추출 실패: 데이터베이스 이름을 가져올 수 없습니다."

            # 테이블 목록
            with self.engine.connect() as conn:
                tables = conn.execute(
                    text(
                        f"""
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = '{db_name}'
                    """
                    )
                ).fetchall()

            schema_text = ""

            for (table_name,) in tables:
                schema_text += f"\nTABLE {table_name}:\n"

                # 컬럼 목록 (ENUM 값 포함)
                with self.engine.connect() as conn:
                    columns = conn.execute(
                        text(
                            f"""
                        SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = '{db_name}'
                        AND TABLE_NAME = '{table_name}'
                        ORDER BY ORDINAL_POSITION
                        """
                        )
                    ).fetchall()

                for col_name, data_type, column_type in columns:
                    if data_type == "enum":
                        # ENUM 값 표시: enum('A','B','C') → (enum: A, B, C)
                        enum_values = column_type.replace("enum(", "").replace(")", "").replace("'", "")
                        schema_text += f"  - {col_name} (enum: {enum_values})\n"
                    else:
                        schema_text += f"  - {col_name} ({data_type})\n"

                # 샘플 데이터 추가
                limit = "" if table_name in CODE_TABLES else f"LIMIT {SAMPLE_LIMIT}"
                with self.engine.connect() as conn:
                    samples = conn.execute(
                        text(f"SELECT * FROM {table_name} {limit}")
                    ).fetchall()

                if samples:
                    schema_text += f"  샘플 데이터:\n"
                    for row in samples:
                        schema_text += f"    {row}\n"

            return schema_text.strip()

        except Exception as e:
            return f"스키마 추출 실패: {e}"
