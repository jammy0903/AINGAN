/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    const backendUrl = process.env.API_URL || "http://localhost:8000";
    return [
      { source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
      { source: "/mcp/:path*", destination: `${backendUrl}/mcp/:path*` },
      { source: "/sitemap.xml", destination: `${backendUrl}/sitemap.xml` },
      { source: "/robots.txt", destination: `${backendUrl}/robots.txt` },
      { source: "/llms.txt", destination: `${backendUrl}/llms.txt` },
      { source: "/.well-known/:path*", destination: `${backendUrl}/.well-known/:path*` },
      { source: "/openapi.json", destination: `${backendUrl}/openapi.json` },
    ];
  },
};

module.exports = nextConfig;
