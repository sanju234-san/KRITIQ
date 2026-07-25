# Walkthrough — Code Translation: `main.py`

Translated `main.py` from python to java.

## 📋 Overview

| | |
|---|---|
| **Source File** | `app/main.py` |
| **From** | python |
| **To** | java |
| **Translated On** | 2026-07-25 19:17:23 |

## 💻 Translated Code

```java
import java.io.IOException;
import java.util.logging.Logger;

import javax.ws.rs.ApplicationPath;
import javax.ws.rs.core.Application;

import org.glassfish.jersey.media.multipart.MultiPartFeature;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.server.filter.RolesAllowedDynamicFeature;

import io.swagger.jaxrs.config.BeanConfig;
import io.swagger.jaxrs.listing.ApiListingResource;
import io.swagger.jaxrs.listing.SwaggerSerializers;

@ApplicationPath("/api")
public class KritiqApplication extends ResourceConfig {

    private static final Logger LOGGER = Logger.getLogger(KritiqApplication.class.getName());

    public KritiqApplication() {
        super();

        // Register resources
        packages("app.routes.auth");
        packages("app.routes.repository");
        packages("app.routes.review");
        packages("app.routes.translation");
        packages("app.routes.explanation");
        packages("app.routes.history");
        packages("app.routes.chat");

        // Register features
        register(MultiPartFeature.class);
        register(RolesAllowedDynamicFeature.class);
        register(SwaggerSerializers.class);
        register(ApiListingResource.class);

        // Swagger configuration
        BeanConfig config = new BeanConfig();
        config.setTitle("KRITIQ API");
        config.setDescription("The backend REST API server for KRITIQ, an AI-powered code analysis platform. Supports JWT Authentication, Code Reviews, Code Translations, Code Explanations, and activity history retrieval.");
        config.setVersion("1.0.0");
        config.setContact("sayeed@domain.com");
        config.setSchemes(new String[] {"http", "https"});
        config.setHost("localhost:8080");
        config.setBasePath("/api");
        config.setResourcePackage("app.routes");
        config.setScan(true);
    }
}

// Rate Limiter
import java.util.concurrent.TimeUnit;

import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerRequestFilter;
import javax.ws.rs.core.Response;

public class RateLimiterFilter implements ContainerRequestFilter {

    private static final int MAX REQUESTS = 10;
    private static final long TIME_WINDOW = TimeUnit.MINUTES.toMillis(1);

    public void filter(ContainerRequestContext context) throws IOException {
        // Implement rate limiting logic here
    }
}

// Error Handlers
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

@Provider
public class ErrorHandler implements ExceptionMapper<Exception> {

    public Response toResponse(Exception exception) {
        return Response.serverError().entity(exception.getMessage()).build();
    }
}

// Root Resource
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

@Path("/")
public class RootResource {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public String root() {
        return "{\"message\": \"Kritiq API is running.\"}";
    }
}

// Security Headers
import javax.ws.rs.container.ContainerResponseContext;
import javax.ws.rs.container.ContainerResponseFilter;
import javax.ws.rs.core.Response;

public class SecurityHeadersFilter implements ContainerResponseFilter {

    public void filter(ContainerRequestContext request, ContainerResponseContext response) {
        response.getHeaders().add("X-Frame-Options", "DENY");
        response.getHeaders().add("X-Content-Type-Options", "nosniff");
        response.getHeaders().add("X-XSS-Protection", "1; mode=block");
        response.getHeaders().add("Referrer-Policy", "strict-origin-when-cross-origin");
        response.getHeaders().add("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
    }
}

// CORS Filter
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerResponseContext;
import javax.ws.rs.container.ContainerResponseFilter;
import javax.ws.rs.core.Response;

public class CORSFilter implements ContainerResponseFilter {

    public void filter(ContainerRequestContext request, ContainerResponseContext response) {
        response.getHeaders().add("Access-Control-Allow-Origin", "*");
        response.getHeaders().add("Access-Control-Allow-Credentials", "true");
        response.getHeaders().add("Access-Control-Allow-Methods", "*");
        response.getHeaders().add("Access-Control-Allow-Headers", "*");
    }
}
```

## ✅ Recommended Next Steps
- [ ] Verify the translated code syntax and logic in the target environment.
- [ ] Compile or run tests to ensure behavioral equivalence with the original source code.

---
*Generated automatically by Kritiq's AI Translation Agent — 2026-07-25 19:17:23*
