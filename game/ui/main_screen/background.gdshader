shader_type canvas_item;
uniform float blur_radius = 4.5;
void fragment() {
    vec4 color = vec4(0.0);
    float total = 0.0;
    for (int x = -4; x <= 4; x++) {
        for (int y = -4; y <= 4; y++) {
            float weight = exp(-float(x*x+y*y)/8.0);
            color += texture(TEXTURE, UV + vec2(float(x),float(y))*TEXTURE_PIXEL_SIZE*blur_radius/2.0)*weight;
            total += weight;
        }
    }
    color /= total;
    float dim = UV.x < 0.5 ? mix(0.86,0.5,UV.x/0.5) : (UV.x < 0.72 ? mix(0.5,0.35,(UV.x-0.5)/0.22) : mix(0.35,0.72,(UV.x-0.72)/0.28));
    COLOR = vec4(mix(color.rgb, vec3(30.0,23.0,26.0)/255.0, dim), 1.0);
}
