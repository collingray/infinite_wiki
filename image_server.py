import torch
from diffusers import AutoPipelineForText2Image, StableCascadeCombinedPipeline
from flask import Flask, request, jsonify, send_file
from io import BytesIO

app = Flask(__name__)

pipe = StableCascadeCombinedPipeline.from_pretrained("stabilityai/stable-cascade", variant="bf16",
                                                     torch_dtype=torch.bfloat16)
pipe.to("cuda")
pipe.prior_image_encoder.to("cuda")


def send_image(image):
    img_io = BytesIO()
    image.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.route('/generate')
def generate():
    """
    Generate and return a new image, using the provided prompt
    """
    prompt = request.args.get('prompt')
    print(prompt)
    if not prompt:
        return jsonify({'error': 'Missing prompt parameter'}), 400

    # Generate the image here
    # image = pipe(prompt=prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
    image = pipe(
        prompt=prompt,
        negative_prompt="",
        num_inference_steps=10,
        prior_num_inference_steps=20,
        prior_guidance_scale=3.0,
        width=768,
        height=1024,
    ).images[0]

    # Return the image
    return send_image(image)


if __name__ == '__main__':
    app.run(debug=False)
