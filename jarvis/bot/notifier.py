import os
from typing import Dict, Any
from aiogram import Bot
from jarvis.core.config import settings

async def send_strategy_alert(strategy_result: Dict[str, Any]):
    """
    Despacha alertas estructuradas al administrador(es) de Telegram
    sobre la acción sugerida y el estado del Circuit Breaker.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN no configurado, omitiendo alerta.")
        return
        
    bot = Bot(token=token)
    
    action = strategy_result.get("action")
    competitor_price = strategy_result.get("competitor_price")
    ideal_price = strategy_result.get("ideal_price")
    suggested_price = strategy_result.get("suggested_price")
    breaker = strategy_result.get("circuit_breaker_tripped")
    filter_amount = strategy_result.get("filter_amount", "N/A")
    competitor_name = strategy_result.get("competitor_name", "Desconocido")
    
    emoji = "🔴" if action == "SELL" else "🟢"
    breaker_msg = "⚠️ <b>CIRCUIT BREAKER ACTIVADO</b> (Se protegió el margen mínimo)\n" if breaker else "✅ Margen Saludable\n"
    
    margin_pct_display = float(settings.min_net_margin_pct) * 100
    
    message = (
        f"{emoji} <b>ALERTA DE ESTRATEGIA - {action}</b> {emoji}\n\n"
        f"🏦 <b>Banco:</b> Banesco\n"
        f"✅ <b>Estatus:</b> Comerciante Verificado\n"
        f"🎯 <b>Filtro Aplicado:</b> {filter_amount} VES\n\n"
        f"🥇 <b>Top 1 ({competitor_name}):</b> {competitor_price} VES\n"
        f"<b>Precio Ideal (-0.01):</b> {ideal_price} VES\n"
        f"<b>Precio Sugerido:</b> <code>{suggested_price}</code> VES\n\n"
        f"💰 <b>Capital Base:</b> {settings.capital_usdt} USDT\n"
        f"📈 <b>Margen Objetivo:</b> {margin_pct_display}%\n\n"
        f"{breaker_msg}"
    )
    
    try:
        for admin_id in settings.admin_telegram_ids:
            await bot.send_message(chat_id=admin_id, text=message, parse_mode="HTML")
    except Exception as e:
        print(f"Error enviando alerta de Telegram: {e}")
    finally:
        await bot.session.close()
