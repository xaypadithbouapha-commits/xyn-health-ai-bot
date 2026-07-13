import logging
import os

from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    text = (
        "ສະບາຍດີ 👋\n"
        "ຂ້ອຍແມ່ນ XYN Health AI Coach v1.0\n\n"
        "ຄຳສັ່ງ:\n"
        "/bmi 74 1.68\n"
        "/workout\n"
        "/meal\n\n"
        "ຫຼືພິມຄຳຖາມສຸຂະພາບໄດ້ເລີຍ."
    )
    await update.message.reply_text(text)


async def bmi(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if len(context.args) != 2:
        await update.message.reply_text(
            "ວິທີໃຊ້: /bmi ນ້ຳໜັກ_kg ສ່ວນສູງ_m\n"
            "ຕົວຢ່າງ: /bmi 74 1.68"
        )
        return

    try:
        weight = float(context.args[0])
        height = float(context.args[1])

        if weight <= 0 or height <= 0:
            raise ValueError

        bmi_value = weight / (height ** 2)

        if bmi_value < 18.5:
            category = "ນ້ຳໜັກຕ່ຳ"
        elif bmi_value < 25:
            category = "ນ້ຳໜັກປົກກະຕິ"
        elif bmi_value < 30:
            category = "ນ້ຳໜັກເກີນ"
        else:
            category = "ອ້ວນ"

        await update.message.reply_text(
            f"BMI: {bmi_value:.1f}\n"
            f"ຜົນ: {category}\n\n"
            "BMI ເປັນພຽງຄ່າປະເມີນເບື້ອງຕົ້ນ."
        )

    except ValueError:
        await update.message.reply_text(
            "ກະລຸນາໃສ່ຕົວເລກທີ່ຖືກຕ້ອງ.\n"
            "ຕົວຢ່າງ: /bmi 74 1.68"
        )


async def workout(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    prompt = """
Create a practical 7-day exercise plan for a 38-year-old man,
74 kg, beginner-to-intermediate fitness level.

Goals:
- improve cardiovascular fitness
- increase VO2 max
- reduce body fat
- protect knees and lower back

Include:
- Zone 2 cardio
- strength training
- recovery days
- session duration
- safety precautions

Respond in Lao language.
"""

    await send_ai_response(update, prompt)


async def meal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    prompt = """
Create a practical 7-day meal plan for a 38-year-old man,
74 kg, who wants gradual fat loss and better heart health.

Requirements:
- common foods available in Laos and Thailand
- high protein
- moderate carbohydrates
- vegetables in every main meal
- avoid extreme dieting
- include estimated portions
- include breakfast, lunch, dinner, and one snack

Respond in Lao language.
"""

    await send_ai_response(update, prompt)


async def health_chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    user_message = update.message.text

    prompt = f"""
You are XYN Health AI Coach.

Give practical, cautious, and easy-to-understand health guidance.
Do not claim to diagnose disease.
Recommend professional medical care for emergencies,
serious symptoms, persistent symptoms, or abnormal vital signs.

The user is a 38-year-old man interested in fitness,
weight management, sleep, recovery, and cardiovascular health.

User question:
{user_message}

Respond in the same language as the user.
"""

    await send_ai_response(update, prompt)


async def send_ai_response(
    update: Update,
    prompt: str,
) -> None:
    waiting_message = await update.message.reply_text(
        "ກຳລັງວິເຄາະ..."
    )

    try:
        response = await client.responses.create(
            model="gpt-5.4-mini",
            input=prompt,
        )

        answer = response.output_text.strip()

        if not answer:
            answer = "ຂໍອະໄພ ບໍ່ສາມາດສ້າງຄຳຕອບໄດ້."

        await waiting_message.edit_text(answer[:4000])

    except Exception:
        logging.exception("OpenAI request failed")
        await waiting_message.edit_text(
            "ເກີດຂໍ້ຜິດພາດໃນການເຊື່ອມ AI. "
            "ກະລຸນາກວດ OPENAI_API_KEY ແລະ Railway Logs."
        )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bmi", bmi))
    app.add_handler(CommandHandler("workout", workout))
    app.add_handler(CommandHandler("meal", meal))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            health_chat,
        )
    )

    logging.info("XYN Health AI Coach started")
    app.run_polling()


if __name__ == "__main__":
    main()
