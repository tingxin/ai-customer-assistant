import random
from datetime import datetime
from typing import Dict, Any

class ChatService:
    def __init__(self):
        self.demo_responses = {
            "text": [
                {"text": "您好！我是智能客服助手，很高兴为您服务！"},
                {"text": "感谢您的咨询，我会尽力帮助您解决问题。"},
                {"text": "这是一个演示回复，展示文本消息功能。"},
                {"text": "我正在学习中，请多多指教！"},
                {"text": "有什么其他问题需要帮助吗？"}
            ],
            "image": [
                {"picUrl": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iIzQyODVGNCIvPjx0ZXh0IHg9IjIwMCIgeT0iMTI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+QUkg5Zu+54mHPC90ZXh0Pjwvc3ZnPg=="},
                {"picUrl": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iIzRDQUY1MCIvPjx0ZXh0IHg9IjIwMCIgeT0iMTI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5pm65oSP5a6i5pyNPC90ZXh0Pjwvc3ZnPg=="},
                {"picUrl": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgZmlsbD0iI0ZGOTgwMCIvPjx0ZXh0IHg9IjIwMCIgeT0iMTI1IiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5ryU56S65Zu+54mHPC90ZXh0Pjwvc3ZnPg=="}
            ],
            "card": [
                {
                    "title": "智能客服系统",
                    "desc": "基于AI技术的智能客服解决方案",
                    "img": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iIzQyODVGNCIvPjx0ZXh0IHg9IjE1MCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5BSeWuouacjTwvdGV4dD48L3N2Zz4=",
                    "actions": [{"type": "url", "text": "了解更多", "url": "#"}]
                },
                {
                    "title": "产品介绍",
                    "desc": "全方位的客服解决方案",
                    "img": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iIzRDQUY1MCIvPjx0ZXh0IHg9IjE1MCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7kuqflk4HkuIvnu40PC90ZXh0Pjwvc3ZnPg==",
                    "actions": [{"type": "url", "text": "查看详情", "url": "#"}]
                },
                {
                    "title": "技术支持",
                    "desc": "7x24小时技术支持服务",
                    "img": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iI0ZGOTgwMCIvPjx0ZXh0IHg9IjE1MCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7mioDmnK/mlK/mjIE8L3RleHQ+PC9zdmc+",
                    "actions": [{"type": "url", "text": "联系我们", "url": "#"}]
                }
            ],
            "list": [
                {
                    "header": {"title": "系统功能"},
                    "items": [
                        {"title": "智能问答", "desc": "基于AI的自动问答", "icon": "🤖"},
                        {"title": "多轮对话", "desc": "支持上下文理解", "icon": "💬"},
                        {"title": "实时监控", "desc": "对话质量监控", "icon": "📊"}
                    ]
                },
                {
                    "header": {"title": "服务特色"},
                    "items": [
                        {"title": "24小时服务", "desc": "全天候在线服务", "icon": "⏰"},
                        {"title": "多语言支持", "desc": "支持多种语言", "icon": "🌍"},
                        {"title": "快速响应", "desc": "秒级响应速度", "icon": "⚡"}
                    ]
                }
            ]
        }
    
    def get_random_response(self, user_message: str = "") -> Dict[str, Any]:
        # 根据用户输入的关键词返回特定类型的消息
        user_message_lower = user_message.lower()
        
        if "卡片" in user_message_lower or "card" in user_message_lower:
            response_type = "card"
        elif "列表" in user_message_lower or "list" in user_message_lower:
            response_type = "list"
        elif "图片" in user_message_lower or "image" in user_message_lower:
            response_type = "image"
        else:
            # 随机选择响应类型：30%文本，30%图片，20%卡片，20%列表
            response_type = random.choices(
                ["text", "image", "card", "list"],
                weights=[30, 30, 20, 20]
            )[0]
        
        content = random.choice(self.demo_responses[response_type])
        
        return {
            "type": response_type,
            "content": content,
            "timestamp": datetime.now()
        }