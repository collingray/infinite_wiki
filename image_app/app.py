import os
import threading

import torch
from diffusers import StableCascadeCombinedPipeline
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

if os.environ.get('IMAGE_PROVIDER') == 'local':
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

elif os.environ.get('IMAGE_PROVIDER') == 'stability':
    stability_api_key = os.environ.get('STABILITY_API_KEY', Exception('Missing STABILITY_API_KEY environment variable'))


    def generate_save_image(path, prompt):

        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
            headers={
                f"authorization": f"Bearer {stability_api_key}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "aspect_ratio": "2:3",
                "model": "sd3-turbo",
                "output_format": "jpeg",
            },
        )

        if response.status_code == 200:
            with open(path, 'wb') as file:
                file.write(response.content)
        else:
            raise Exception(str(response.json()))

else:
    raise ValueError(f"Invalid IMAGE_PROVIDER '{os.environ.get('IMAGE_PROVIDER')}': must be 'local' or 'stability'")


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
