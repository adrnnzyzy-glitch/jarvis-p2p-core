import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Filter
from jarvis.core.config import settings
from jarvis.api.binance import BinanceP2PClient

# 1. Configuración de Componentes
# Obtener el token directamente del entorno o config
token = os.environ.get("EXECUTOR_TELEGRAM_TOKEN", settings.executor_telegram_token)
if not token:
    print("ADVERTENCIA: EXECUTOR_TELEGRAM_TOKEN no configurado.")
    # Token ficticio para evitar caídas inmediatas en el ejemplo
    token = "987654321:ABCDEF1234567890abcdef1234567890abc"

bot = Bot(token=token)
dp = Dispatcher()

# Inicializamos el cliente de Binance P2P (Mock)
binance_client = BinanceP2PClient(merchant_id=settings.binance_merchant_id)

# 2. Filtro de Seguridad (Solo Administradores)
class IsAdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.admin_telegram_ids

# 3. Flujo Principal: Recepción de Comprobantes
@dp.message(F.photo, IsAdminFilter())
async def handle_receipt_upload(message: Message):
    """
    Escucha imágenes de los administradores (comprobantes de pago).
    """
    status_msg = await message.answer("⏳ Recibido comprobante. Consultando órdenes activas en Binance...")
    
    try:
        # A. Identificar Orden Activa
        active_orders = await binance_client.get_active_orders()
        if not active_orders:
            await status_msg.edit_text("❌ No se encontraron órdenes en estado 'Pendiente de Pago'.")
            return
            
        # Tomamos la primera orden activa (en un flujo real, quizás haya que validar montos o usar texto del caption para mapear)
        target_order = active_orders[0]
        order_id = target_order["orderNumber"]
        
        await status_msg.edit_text(f"⏳ Orden encontrada ({order_id}). Descargando recibo...")
        
        # B. Descargar la imagen
        photo = message.photo[-1] # Mayor resolución
        file_path = f"temp_receipt_{order_id}.jpg"
        await bot.download(photo, destination=file_path)
        
        await status_msg.edit_text("⏳ Subiendo comprobante al chat de Binance...")
        
        # C. Cargar comprobante y enviar mensaje
        await binance_client.upload_receipt_to_chat(order_id, file_path)
        
        mensaje_chat = "¡Hola! Pago realizado exitosamente desde titular verificado. Adjunto comprobante. Procedo a marcar la orden como pagada."
        await binance_client.send_chat_message(order_id, mensaje_chat)
        
        await status_msg.edit_text("⏳ Marcando orden como PAGADA oficialmente...")
        
        # D. Marcar orden como pagada
        await binance_client.mark_order_paid(order_id)
        
        # Limpieza de archivo temporal
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # E. Confirmación Final
        await status_msg.edit_text(f"✅ Recibo subido y orden {order_id} marcada como pagada en Binance.")
        
    except Exception as e:
        await status_msg.edit_text(f"⚠️ Ocurrió un error en la ejecución: {str(e)}")


async def main():
    print("Iniciando EXECUTOR BOT (Microservicio de Gestión de Comprobantes)...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Apagando EXECUTOR BOT...")
