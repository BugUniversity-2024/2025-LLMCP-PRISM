"""
Image Adapter - 负责图像生成
阶段 1: Mock 实现（使用 picsum.photos）
阶段 2: 接入 Gemini Flash Image API
"""
import httpx
import random
from pathlib import Path
from typing import Dict, Any, Optional


class ImageAdapter:
    """图像生成适配器（阶段 1: Mock 实现）"""

    def __init__(self, use_real_api: bool = False):
        """
        Args:
            use_real_api: 是否使用真实 Gemini API（阶段 2 设置为 True）
        """
        self.use_real_api = use_real_api
        if use_real_api:
            import google.generativeai as genai
            from app.config import settings
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)

        # 存储路径
        from app.config import settings
        self.storage_path = Path(settings.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def generate_image(
        self,
        prompt: str,
        session_id: str,
        version: int,
        reference_image_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        生成图片

        Args:
            prompt: 自然语言 Prompt
            session_id: 会话 ID
            version: 版本号
            reference_image_path: 参考图片路径（用于迭代优化）

        Returns:
            {
                "image_url": "http://localhost:8000/images/xxx.png",
                "image_path": "/path/to/storage/xxx.png"
            }

        Raises:
            RuntimeError: API 调用失败
        """
        if self.use_real_api:
            return await self._generate_with_gemini(prompt, session_id, version, reference_image_path)
        else:
            return await self._generate_mock(session_id, version)

    async def _generate_mock(self, session_id: str, version: int) -> Dict[str, str]:
        """阶段 1: Mock 实现（下载 picsum 图片）"""
        try:
            # 使用随机种子确保图片不同
            seed = random.randint(1, 10000)
            picsum_url = f"https://picsum.photos/seed/{seed}/1920/1080"

            # 文件命名
            filename = f"{session_id}-v{version}.png"
            filepath = self.storage_path / filename

            # 下载图片
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(picsum_url, follow_redirects=True)
                response.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(response.content)

            # 构建公开 URL
            public_url = f"http://localhost:8000/images/{filename}"

            return {
                "image_url": public_url,
                "image_path": str(filepath)
            }

        except httpx.HTTPError as e:
            raise RuntimeError(f"图片下载失败: {e}")
        except Exception as e:
            raise RuntimeError(f"图片生成失败: {e}")

    async def _generate_with_gemini(
        self,
        prompt: str,
        session_id: str,
        version: int,
        reference_image_path: Optional[str] = None
    ) -> Dict[str, str]:
        """阶段 2: 真实 Gemini API 调用"""
        try:
            # TODO: 实现 Gemini Flash Image 调用
            # 注意：需要确认 Gemini 是否支持 text-to-image 和 image-to-image

            # 构建请求
            content_parts = [prompt]

            # 如果有参考图片（迭代场景）
            if reference_image_path:
                with open(reference_image_path, "rb") as f:
                    image_data = f.read()
                content_parts.append({
                    "mime_type": "image/png",
                    "data": image_data
                })

            # 调用 Gemini API
            response = self.model.generate_content(content_parts)

            # 提取图片（需要确认响应格式）
            # 假设返回 base64 编码的图片
            if hasattr(response, 'image_data'):
                image_data = response.image_data
            else:
                raise RuntimeError("Gemini 响应中未找到图片数据")

            # 保存图片
            filename = f"{session_id}-v{version}.png"
            filepath = self.storage_path / filename

            import base64
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(image_data))

            public_url = f"http://localhost:8000/images/{filename}"

            return {
                "image_url": public_url,
                "image_path": str(filepath)
            }

        except Exception as e:
            raise RuntimeError(f"Gemini 图片生成失败: {e}")
