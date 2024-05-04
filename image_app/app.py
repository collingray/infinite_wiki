import threading

import torch
from diffusers import StableCascadeCombinedPipeline
from flask import Flask, request, jsonify

app = Flask(__name__)

pipe = StableCascadeCombinedPipeline.from_pretrained("stabilityai/stable-cascade", variant="bf16",
                                                     torch_dtype=torch.bfloat16)
pipe.to("cuda")
pipe.prior_image_encoder.to("cuda")


def generate_save_image(path, prompt):
    image = pipe(
        prompt=prompt,
        negative_prompt="",
        num_inference_steps=10,
        prior_num_inference_steps=20,
        prior_guidance_scale=3.0,
        width=768,
        height=1024,
    ).images[0]

    image.save(path)


@app.route('/generate')
def generate():
    """
    Generate an image from the prompt, store it in static/images, and return the image path.

    The image path is returned immediately, but the image is generated in the background.
    """
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({'error': 'Missing prompt parameter'}), 400

    path = f'static/images/{abs(hash(prompt))}.jpg'

    # Generate and save the image in the background
    threading.Thread(target=generate_save_image, args=(path, prompt)).start()

    # Return the image
    return jsonify({'path': path})


if __name__ == '__main__':
    app.run(debug=False, port=5000)
