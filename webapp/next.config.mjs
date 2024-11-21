/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [{ hostname: "i.ibb.co" }, { hostname: "pure.itu.dk" }],
  },
};

export default nextConfig;
