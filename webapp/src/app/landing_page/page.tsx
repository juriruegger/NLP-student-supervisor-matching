import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-2xl font-bold">SaaSify</h1>
          <nav>
            <ul className="flex space-x-4">
              <li><a href="#features" className="hover:underline">Features</a></li>
              <li><a href="#pricing" className="hover:underline">Pricing</a></li>
              <li><a href="#contact" className="hover:underline">Contact</a></li>
            </ul>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <section className="text-center py-16">
          <h2 className="text-4xl font-bold mb-4">Boost Your Productivity with SaaSify</h2>
          <p className="text-gray-600 mb-6">Streamline your business operations with our powerful tools and integrations.</p>
          <Button className="text-xl px-6 py-3">Get Started</Button>
        </section>

        {/* Features Section */}
        <section id="features" className="py-12">
          <h3 className="text-3xl font-bold text-center mb-6">Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card>
              <CardContent>
                <h4 className="font-bold text-xl">Feature One</h4>
                <p className="text-gray-600">Description of feature one that highlights its value.</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <h4 className="font-bold text-xl">Feature Two</h4>
                <p className="text-gray-600">Description of feature two that makes it unique.</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <h4 className="font-bold text-xl">Feature Three</h4>
                <p className="text-gray-600">Description of feature three and its benefits.</p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-12 bg-gray-100">
          <h3 className="text-3xl font-bold text-center mb-6">Pricing</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card>
              <CardContent>
                <h4 className="font-bold text-xl">Basic Plan</h4>
                <p className="text-gray-600">$10/month</p>
                <Button className="mt-4">Choose Plan</Button>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <h4 className="font-bold text-xl">Pro Plan</h4>
                <p className="text-gray-600">$30/month</p>
                <Button className="mt-4">Choose Plan</Button>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <h4 className="font-bold text-xl">Enterprise Plan</h4>
                <p className="text-gray-600">Contact us</p>
                <Button className="mt-4">Choose Plan</Button>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Contact Section */}
        <section id="contact" className="py-12">
          <h3 className="text-3xl font-bold text-center mb-6">Get in Touch</h3>
          <form className="max-w-lg mx-auto space-y-4">
            <input
              type="text"
              placeholder="Your Name"
              className="w-full px-4 py-2 border rounded-md"
            />
            <input
              type="email"
              placeholder="Your Email"
              className="w-full px-4 py-2 border rounded-md"
            />
            <textarea
              placeholder="Your Message"
              rows={4}
              className="w-full px-4 py-2 border rounded-md"
            ></textarea>
            <Button type="submit" className="w-full">Submit</Button>
          </form>
        </section>
      </main>

      <footer className="bg-gray-800 text-white py-6">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2025 SaaSify. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
