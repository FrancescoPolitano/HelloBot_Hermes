package com.grazianomarallo.RestfulService;

/**
 * Created by grazianomarallo on 11/11/2017.
 */
import jdk.nashorn.internal.parser.JSONParser;
import jdk.nashorn.internal.runtime.JSONFunctions;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;

// The Java class will be hosted at the URI path "/restresources"
@Path("/restresources")
public class RestResources {
    // The Java method will process HTTP GET requests
    @GET
    // The Java method will produce content identified by the MIME Media type "text/plain"
    @Produces("text/plain")
    public String getClichedMessage() {
        // Return some cliched textual content
        return "Hello World";
    }


    @GET
    // The Java method will produce content identified by the MIME Media type "text/plain"
    @Produces("text/plain")
    public String getCafeterias() {
        // Return some cliched textual content
        return new JSONParser();
    }

    @GET
    // The Java method will produce content identified by the MIME Media type "text/plain"
    @Produces("text/plain")
    public String getClassrooms() {
        // Return some cliched textual content
        return "Hello World";
    }

    @GET
    // The Java method will produce content identified by the MIME Media type "text/plain"
    @Produces("text/plain")
    public String getLabs() {
        // Return some cliched textual content
        return "Hello World";
    }






}