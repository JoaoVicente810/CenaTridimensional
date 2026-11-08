#version 330 core
in vec3 vWorldPosition;
in vec3 vNormal;
in vec2 vUV;
in vec4 vLightPosition;

uniform vec3 uBaseColor;
uniform vec3 uLightDirection;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;
uniform vec3 uCameraPosition;
uniform bool uUseTexture;
uniform sampler2D uTexture;
uniform sampler2D uShadowMap;
uniform float uShadowStrength;

out vec4 fragColor;

float calculateShadow(vec4 lightPosition, vec3 normal, vec3 lightDir) {
    vec3 projected = lightPosition.xyz / lightPosition.w;
    projected = projected * 0.5 + 0.5;
    if (projected.z > 1.0 || projected.x < 0.0 || projected.x > 1.0 ||
        projected.y < 0.0 || projected.y > 1.0) {
        return 0.0;
    }

    float bias = max(0.0018 * (1.0 - dot(normal, lightDir)), 0.00035);
    vec2 texelSize = 1.0 / vec2(textureSize(uShadowMap, 0));
    float shadow = 0.0;
    for (int x = -1; x <= 1; ++x) {
        for (int y = -1; y <= 1; ++y) {
            float closestDepth = texture(uShadowMap,
                projected.xy + vec2(x, y) * texelSize).r;
            shadow += (projected.z - bias > closestDepth) ? 1.0 : 0.0;
        }
    }
    shadow /= 9.0;
    return shadow * uShadowStrength;
}

void main() {
    vec3 albedo = uBaseColor;
    if (uUseTexture) {
        albedo *= texture(uTexture, vUV).rgb;
    }

    vec3 normal = normalize(vNormal);
    vec3 lightDir = normalize(-uLightDirection);
    float diffuse = max(dot(normal, lightDir), 0.0);

    vec3 viewDir = normalize(uCameraPosition - vWorldPosition);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float specular = pow(max(dot(normal, halfwayDir), 0.0), 32.0) * 0.18;

    float shadow = calculateShadow(vLightPosition, normal, lightDir);
    vec3 lighting = uAmbientColor + (1.0 - shadow) *
                    (uLightColor * (diffuse + specular));
    fragColor = vec4(albedo * lighting, 1.0);
}
