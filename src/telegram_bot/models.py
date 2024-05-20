import numpy as np
from transformers import pipeline


class BertModel:
    def __init__(self, model_name, chunk_size=512, stride=256):
        self.pipe = pipeline("text-classification", model=model_name)
        self.chunk_size = chunk_size
        self.stride = stride

    def run(self, text: str):
        # Split the text into chunks
        chunks = self._chunk_text(text)
        # Get predictions for each chunk
        results = [self.pipe(chunk)[0] for chunk in chunks]
        # Combine the results
        combined_result = self._combine_results(results)
        return combined_result

    def _chunk_text(self, text: str):
        """Split the text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            start += self.stride
        return chunks

    def _combine_results(self, results):
        """Combine the results by averaging the scores."""
        labels = list(set(result['label'] for result in results))
        scores = {label: [] for label in labels}

        for result in results:
            scores[result['label']].append(result['score'])

        # Average the scores for each label
        avg_scores = {label: np.mean(scores[label]) for label in scores}

        # Find the label with the highest average score
        combined_label = max(avg_scores, key=avg_scores.get)
        combined_score = avg_scores[combined_label]

        return {'label': combined_label, 'score': combined_score}


class LLM:
    def __init__(self):
        import fireworks.client
        API_KEY = "harmvuNWlUxCBNLqkG4O0F0IZLaI0ZlkNWE95wLtJ1T2xkqi"
        self.client = fireworks.client
        fireworks.client.api_key = API_KEY
        self.prompt = lambda document: f"""
            Твоя задача сообщить, является ли следующий текст фейковой новостью. Дополнительно, сообщи почему ты так считаешь.
            
            Текст новости: {document}
            """
    def run(self, text: str, max_length=50):
        completion = self.client.Completion.create(
            model="accounts/fireworks/models/mixtral-8x7b-instruct",
            prompt=self.prompt(text),
            max_tokens=250,
            temperature=0.1,
            top_p=1,
            top_k=40
        )
        return completion.choices[0].text