import aiohttp

TITO_API_ROOT = "https://api.tito.io/v3"


class TitoAPIError(Exception):
    pass


class TitoAPI:
    def __init__(self, api_token: str, account_slug: str, event_slug: str):
        self.url_base = f"{TITO_API_ROOT}/{account_slug}/{event_slug}"
        self.base_headers = {
            "Authorization": f"Token token={api_token}",
            "Accept": "application/json"
        }

    async def fetch_question_answers(self, question_slug: str) -> list[dict]:
        endpoint = f"{self.url_base}/questions/{question_slug}/answers"

        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, headers=self.base_headers) as response:
                answers = await response.json()
                return [TitoAnswer.from_json(a) for a in answers.get("answers", [])]


class TitoAPIObject:
    TYPE: str

    @classmethod
    def from_json(cls, data: dict):
        raise NotImplementedError("This method must be overridden in the child class.")


class TitoAnswer(TitoAPIObject):
    TYPE = "answer"

    def __init__(self, answer_id: int, ticket_id: int, response: str):
        self.answer_id = answer_id
        self.ticket_id = ticket_id
        self.response = response

    @classmethod
    def from_json(cls, data: dict):
        if answer_type := data.get("_type") != TitoAnswer.TYPE:
            raise TitoAPIError(f"Invalid object type, expected '{TitoAnswer.TYPE}', got '{answer_type}'")

        answer_id = data.get("id")
        ticket_id = data.get("ticket_id")
        response = data.get("response")

        return cls(answer_id, ticket_id, response)
