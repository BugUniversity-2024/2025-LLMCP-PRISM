"""
Image Adapter - 负责图像生成
阶段 1: Mock 实现（使用 picsum.photos）
阶段 2: 接入火山引擎 Seedream 图片生成 API
"""
import httpx
import random
from pathlib import Path
from typing import Dict, Any, Optional


class ImageAdapter:
    """图像生成适配器

    阶段 1: Mock 实现（使用 picsum.photos）
    阶段 2: 接入火山引擎 Seedream API
    """

    def __init__(self, use_real_api: bool = False):
        """
        Args:
            use_real_api: 是否使用真实火山引擎 API（阶段 2 设置为 True）
        """
        self.use_real_api = use_real_api

        # 存储路径
        from app.config import settings
        self.storage_path = Path(settings.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 初始化火山引擎客户端（使用 OpenAI SDK 兼容接口）
        if use_real_api:
            from openai import OpenAI

            # 使用 OpenAI SDK 调用火山引擎 Seedream API
            self.client = OpenAI(
                api_key=settings.gemini_api_key,
                base_url=settings.gemini_api_base
            )
            self.model = settings.gemini_model

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
            from app.config import settings
            public_url = f"{settings.public_base_url}/images/{filename}"

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
        """调用火山引擎 Seedream 图片生成 API（OpenAI SDK 兼容接口）"""
        try:
            print(f"🔄 调用火山引擎 Seedream 图片生成 API...")

            # 使用 OpenAI 图片生成接口格式
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size="2K",  # 火山引擎支持: "2K", "4K" 或像素值如 "2048x2048"
                response_format="url",  # 返回 URL，或使用 "b64_json" 返回 base64
                extra_body={
                    "watermark": False  # 是否添加水印
                }
            )

            # 获取图片 URL
            image_url = response.data[0].url

            # 下载图片到本地
            filename = f"{session_id}-v{version}.png"
            filepath = self.storage_path / filename

            async with httpx.AsyncClient(timeout=60.0) as client:
                img_response = await client.get(image_url)
                img_response.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(img_response.content)

            from app.config import settings
            public_url = f"{settings.public_base_url}/images/{filename}"

            print(f"✅ 火山引擎图片生成成功: {filename}")
            return {
                "image_url": public_url,
                "image_path": str(filepath)
            }

        except Exception as e:
            print(f"❌ 火山引擎图片生成失败: {e}")
            print(f"⚠️ 回退到 mock 模式")
            return await self._generate_mock(session_id, version)
