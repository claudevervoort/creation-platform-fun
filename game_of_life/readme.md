Game Of Life
-------------

See Fabric Engine for information on Creation Platform: http://fabric-engine.com

This code is running of the latest beta 1.0.31 and needs one change in CP code GeometryInstance.kl `setInstanceData` to run:

    transformKey.index = 0;
    transformKey.type = RenderValue_uniform;
    if(transformIndex==-1){
        renderParams.layers[2][0].uniforms[0].setAsMat44( transforms.size(), OGLShaderProgramUniformReferential_world ); //new line
        renderParams.layers[2][0].uniforms[0].perElementValueVersion.resize( transforms.size() ); //new line
        for( Size i = 0; i < transforms.size(); ++i )
            renderParams.layers[2][0].set( transformKey, transforms[ i ].toMat44(), i );
