function handler(event) {
    var request = event.request;
    var uri = request.uri;
    
    // Check if the path starts with any of the partner-specific paths
    if (uri.startsWith('/api/tymebank/hello') || uri.startsWith('/api/sanlam/hello')) {
        // Store the original URI for reference
        var originalUri = uri;
        
        // Extract any additional path components or query parameters
        var pathSegments = uri.split('/');
        
        // Rewrite to the generic path
        request.uri = '/api/abc/hello';
        
        // Add a header to track the original path (optional, helps with debugging)
        if (!request.headers) {
            request.headers = {};
        }
        request.headers['x-original-path'] = {value: originalUri};
        
        // Log the rewrite (visible in CloudWatch Logs if you enable logging)
        console.log('Path rewritten from ' + originalUri + ' to ' + request.uri);
    }
    
    return request;
} 