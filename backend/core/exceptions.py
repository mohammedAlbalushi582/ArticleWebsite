from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException


class ApplicationError(APIException):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.status_code = status_code
        self.detail = {"error": {"code": code, "message": message}}
        super().__init__(detail=self.detail)


class ArticleNotFound(ApplicationError):
    def __init__(self):
        super().__init__("ERR_ARTICLE_NOT_FOUND", "Article not found.", 404)


class ArticleFetchFailed(ApplicationError):
    def __init__(self, message: str = "Failed to fetch article from URL."):
        super().__init__("ERR_ARTICLE_FETCH_FAILED", message)


class AnalysisFailed(ApplicationError):
    def __init__(self, message: str = "AI analysis failed. Please try again."):
        super().__init__("ERR_ANALYSIS_FAILED", message)



def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and "error" not in response.data:
        # Wrap DRF's default errors into our format
        response.data = {
            "error": {
                "code": f"ERR_{response.status_code}",
                "message": response.data,
            }
        }

    return response
