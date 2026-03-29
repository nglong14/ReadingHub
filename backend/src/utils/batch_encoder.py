import asyncio
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class BatchEncoder:
    def __init__(self, model, max_batch_size: int = 32, max_wait_ms: int = 50):
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_wait_seconds = max_wait_ms / 1000.0
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None
        self._stop_marker = object()

    def start(self):
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self):
        if self._worker_task is None:
            return
        await self._queue.put(self._stop_marker)
        try:
            await self._worker_task
        finally:
            self._worker_task = None

    async def submit(self, text: str) -> List[float]:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        await self._queue.put((text, future))
        return await future

    async def _worker_loop(self):
        while True:
            item = await self._queue.get()
            if item is self._stop_marker:
                break

            batch_texts: List[str] = []
            batch_futures: List[asyncio.Future] = []
            saw_stop_marker = False

            text, future = item
            batch_texts.append(text)
            batch_futures.append(future)

            loop = asyncio.get_running_loop()
            deadline = loop.time() + self.max_wait_seconds

            while len(batch_texts) < self.max_batch_size:
                timeout = deadline - loop.time()
                if timeout <= 0:
                    break

                try:
                    next_item = await asyncio.wait_for(self._queue.get(), timeout=timeout)
                except asyncio.TimeoutError:
                    break

                if next_item is self._stop_marker:
                    saw_stop_marker = True
                    break

                next_text, next_future = next_item
                batch_texts.append(next_text)
                batch_futures.append(next_future)

            try:
                vectors = await loop.run_in_executor(
                    None,
                    self._encode_batch,
                    batch_texts,
                )
                for future, vector in zip(batch_futures, vectors):
                    if not future.done():
                        future.set_result(vector)
            except Exception as exc:
                logger.exception("Batch encoding failed")
                for future in batch_futures:
                    if not future.done():
                        future.set_exception(exc)

            if saw_stop_marker:
                break

    def _encode_batch(self, texts: List[str]) -> List[List[float]]:
        encoded = self.model.encode(texts, normalize_embeddings=True)
        return encoded.tolist()
