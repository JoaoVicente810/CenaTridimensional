#version 330 core
layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec2 aUV;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;
uniform mat4 uLightSpace;

out vec3 vWorldPosition;
out vec3 vNormal;
out vec2 vUV;
out vec4 vLightPosition;

void main() {
    vec4 worldPosition = uModel * vec4(aPosition, 1.0);
    vWorldPosition = worldPosition.xyz;
    vNormal = mat3(transpose(inverse(uModel))) * aNormal;
    vUV = aUV;
    vLightPosition = uLightSpace * worldPosition;
    gl_Position = uProjection * uView * worldPosition;
}
