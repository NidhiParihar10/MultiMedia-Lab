import os
from f5_tts.api import F5TTS



def main():
    print("================================")
    print("VOICE CLONING")
    print("================================")

    reference_audio = input("Enter reference audio path: ").strip().strip('"').strip("'")
    reference_text = input("Enter reference audio transcript: ").strip()
    target_text = input("Enter text to generate: ").strip()

    if not os.path.isfile(reference_audio):
        print("Error: Reference audio file does not exist.")
        return

    if not target_text:
        print("Error: Target text cannot be empty.")
        return

    os.makedirs("output", exist_ok=True)
    output_file = os.path.join("output", "cloned_voice.wav")

    try:
        print("\nLoading F5-TTS model...")
        f5tts = F5TTS()

        print("Generating cloned voice...")

        f5tts.infer(
            ref_file=reference_audio,
            ref_text=reference_text,
            gen_text=target_text,
            file_wave=output_file,
            nfe_step=8
        )

        print("\n================================")
        print("VOICE CLONING COMPLETE")
        print("================================")
        print(f"Reference Audio : {os.path.basename(reference_audio)}")
        print(f"Output File     : {output_file}")
        print("\nUse only your own voice or a voice you have permission to clone.")

    except Exception as error:
        print(f"\nError while cloning voice: {error}")


if __name__ == "__main__":
    main()
