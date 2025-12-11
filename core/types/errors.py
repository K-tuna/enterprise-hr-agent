"""
Custom Errors
HR Agent 커스텀 예외 정의
"""


class HRAgentError(Exception):
    """HR Agent 기본 예외"""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code}, message={self.message})"


class SQLExecutionError(HRAgentError):
    """SQL 실행 오류"""

    def __init__(self, message: str, sql: str = ""):
        super().__init__(message, "SQL_EXECUTION_ERROR")
        self.sql = sql


class RAGRetrievalError(HRAgentError):
    """RAG 검색 오류"""

    def __init__(self, message: str):
        super().__init__(message, "RAG_RETRIEVAL_ERROR")


class RouterError(HRAgentError):
    """라우팅 오류"""

    def __init__(self, message: str):
        super().__init__(message, "ROUTER_ERROR")


class DatabaseConnectionError(HRAgentError):
    """DB 연결 오류"""

    def __init__(self, message: str):
        super().__init__(message, "DATABASE_CONNECTION_ERROR")
