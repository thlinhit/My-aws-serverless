function handler(event) {
    var request = event.request;
    var uri = request.uri;
    
    // Check for specific paths to rewrite
    if (uri.startsWith('/api/tymebank/hello') || uri.startsWith('/api/sanlam/hello')) {
        // Extract the part after '/api/partner/'
        var pathParts = uri.split('/');
        
        // Rewrite to /api/abc/hello
        request.uri = '/api/abc/hello';
        
        // Log the rewrite (visible in CloudWatch Logs if you enable logging)
        console.log('Path rewritten from ' + uri + ' to ' + request.uri);
    }
    
    return request;
} 