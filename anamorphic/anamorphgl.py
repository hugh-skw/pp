"""
anamorphgl.py

An OpenGL program that does anamorphic projection.

Author: Mahesh Venkitachalam
"""

import OpenGL
from OpenGL.GL import *

import numpy, math, sys, os
import glutils

import cyglfw3 as glfw

strVS = """
#version 330 core

layout(location = 0) in vec3 aVert;

uniform mat4 uMVMatrix;
uniform mat4 uPMatrix;
uniform float uTheta;
uniform bool showProjection;

out vec2 vTexCoord;
out vec4 vColor;

void main() {

  vec3 P = aVert;
  vColor = vec4(0.0, 1.0, 0.0, 1.0);

  if (showProjection) {
    float R = 1.0;
    vec3 E = vec3(0.0, 5.0, 8.0);
    vec3 N = vec3(aVert.xy/R, 0.0);
    vec3 I = aVert;
    vec3 d1 = normalize(I-E);
    vec3 d2 = normalize(d1 - 2*dot(d1, N)*N);
    float t = -I.z/d2.z;
    P = I + d2*t;
    vColor = vec4(1.0, 0.0, 0.0, 1.0);
  }

  // transform vertex
  gl_Position = uPMatrix * uMVMatrix * vec4(P, 1.0); 
  // set texture coord
  vTexCoord = aVert.xy + vec2(0.5, 0.5);
}
"""
strFS = """
#version 330 core

in vec2 vTexCoord;
in vec4 vColor;

uniform sampler2D tex2D;

out vec4 fragColor;

void main() {
     fragColor = vColor;
     //fragColor = texture(tex2D, vTexCoord);
}
"""

class Scene:    
    """ OpenGL 3D scene class"""
    # initialization
    def __init__(self):
        # create shader
        self.program = glutils.loadShaders(strVS, strFS)

        glUseProgram(self.program)

        self.pMatrixUniform = glGetUniformLocation(self.program, 
                                                   'uPMatrix')
        self.mvMatrixUniform = glGetUniformLocation(self.program, 
                                                  "uMVMatrix")
        # texture 
        self.tex2D = glGetUniformLocation(self.program, "tex2D")

        # define triange strip vertices 
        R = 1.0
        nR = 20
        H = 4.0
        nH = 40        
        vertexData = numpy.zeros(3*nR*nH, numpy.float32).reshape(nR*nH, 3)
        angles = numpy.linspace(0, math.pi, nR)
        heights = numpy.linspace(0, H, nH)
        i = 0
        for h in heights:
            for t in angles:
                x = R*math.cos(t)
                y = R*math.sin(t)
                z = h
                vertexData[i] = [x, y, z]
                i += 1
        vertexData.resize(3*nR*nH, 1)
        self.nVert = nR*nH

        # set up vertex array object (VAO)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        # vertices
        self.vertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffer)
        # set buffer data 
        glBufferData(GL_ARRAY_BUFFER, 4*len(vertexData), vertexData, 
                     GL_STATIC_DRAW)
        # enable vertex array
        glEnableVertexAttribArray(0)
        # set buffer data pointer
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        """
        # individual triangles
        indices = numpy.array([0, 1, 2, 3], numpy.int16)
        self.nIndices = indices.size;

        # index buffer
        self.indexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer);
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 2*len(indices), indices, 
                     GL_STATIC_DRAW)
        # index
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer)
        """

        # unbind VAO
        glBindVertexArray(0)

        # time
        self.t = 0 

        # texture
        self.texId = glutils.loadTexture('star.png')

    # step
    def step(self):
        # increment angle
        self.t = (self.t + 1) % 360
        # set shader angle in radians
        glUniform1f(glGetUniformLocation(self.program, 'uTheta'), 
                    math.radians(self.t))

    # render 
    def render(self, pMatrix, mvMatrix):        
        # use shader
        glUseProgram(self.program)
        
        # set proj matrix
        glUniformMatrix4fv(self.pMatrixUniform, 1, GL_FALSE, pMatrix)

        # set modelview matrix
        glUniformMatrix4fv(self.mvMatrixUniform, 1, GL_FALSE, mvMatrix)


        # enable texture 
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texId)
        glUniform1i(self.tex2D, 0)

        # bind VAO
        glBindVertexArray(self.vao)
        # draw
        #glDrawElements(GL_TRIANGLE_STRIP, self.nIndices, 
         #              GL_UNSIGNED_SHORT, None)
        glPointSize(2.0)

        # draw cylinder
        glUniform1i(glGetUniformLocation(self.program, 'showProjection'), 
                    False)
        glDrawArrays(GL_POINTS, 0, self.nVert)

        # draw projection
        glUniform1i(glGetUniformLocation(self.program, 'showProjection'), 
                    True)
        glDrawArrays(GL_POINTS, 0, self.nVert)

        # unbind VAO
        glBindVertexArray(0)


class RenderWindow:
    """GLFW Rendering window class"""
    def __init__(self):

        # save current working directory
        cwd = os.getcwd()

        # initialize glfw - this changes cwd
        glfw.Init()
        
        # restore cwd
        os.chdir(cwd)

        # version hints
        glfw.WindowHint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.WindowHint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.WindowHint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        glfw.WindowHint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    
        # make a window
        self.width, self.height = 640, 480
        self.aspect = self.width/float(self.height)
        self.win = glfw.CreateWindow(self.width, self.height, "anamorphic")
        # make context current
        glfw.MakeContextCurrent(self.win)
        
        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.5, 0.5,1.0)

        # set window callbacks
        glfw.SetMouseButtonCallback(self.win, self.onMouseButton)
        glfw.SetKeyCallback(self.win, self.onKeyboard)
        glfw.SetWindowSizeCallback(self.win, self.onSize)        

        # create 3D
        self.scene = Scene()

        # exit flag
        self.exitNow = False

        
    def onMouseButton(self, win, button, action, mods):
        #print 'mouse button: ', win, button, action, mods
        pass

    def onKeyboard(self, win, key, scancode, action, mods):
        #print 'keyboard: ', win, key, scancode, action, mods
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE: 
                self.exitNow = True
        
    def onSize(self, win, width, height):
        #print 'onsize: ', win, width, height
        self.width = width
        self.height = height
        self.aspect = width/float(height)
        glViewport(0, 0, self.width, self.height)

    def run(self):
        # initializer timer
        glfw.SetTime(0.0)
        t = 0.0
        while not glfw.WindowShouldClose(self.win) and not self.exitNow:
            # update every x seconds
            currT = glfw.GetTime()
            if currT - t > 0.1:
                # update time
                t = currT
                # clear
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                
                # build projection matrix
                pMatrix = glutils.perspective(45.0, self.aspect, 0.1, 100.0)
                
                mvMatrix = glutils.lookAt([0.0, 4.0, 10.0], [0.0, 2.0, 2.0],
                                          [0.0, -1.0, 0.0])
                # render
                self.scene.render(pMatrix, mvMatrix)
                # step 
                self.scene.step()

                glfw.SwapBuffers(self.win)
                # Poll for and process events
                glfw.PollEvents()
        # end
        glfw.Terminate()

# main() function
def main():
    print 'starting anamorphic...'    
    rw = RenderWindow()
    rw.run()

# call main
if __name__ == '__main__':
    main()