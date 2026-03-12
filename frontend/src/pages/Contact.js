import React, { useState } from 'react';
import { Mail, Phone, MapPin, Clock, Send, MessageSquare, PhoneCall, Users } from 'lucide-react';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: '',
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, this would send the data to a backend
    console.log('Form submitted:', formData);
    setSubmitted(true);
  };

  const contactInfo = [
    {
      icon: MapPin,
      title: 'Address',
      details: ['123 Community Street', 'New Delhi, India'],
    },
    {
      icon: Phone,
      title: 'Phone',
      details: ['+91 98765 43210', '+91 98765 43211'],
    },
    {
      icon: Mail,
      title: 'Email',
      details: ['contact@activ.org.in', 'support@activ.org.in'],
    },
    {
      icon: Clock,
      title: 'Working Hours',
      details: ['Mon - Fri: 9:00 AM - 6:00 PM', 'Sat: 9:00 AM - 2:00 PM'],
    },
  ];

  const departments = [
    {
      icon: Users,
      title: 'General Inquiries',
      email: 'info@activ.org.in',
      description: 'Questions about membership and community',
    },
    {
      icon: MessageSquare,
      title: 'Events',
      email: 'events@activ.org.in',
      description: 'Event registrations and partnerships',
    },
    {
      icon: PhoneCall,
      title: 'Support',
      email: 'support@activ.org.in',
      description: 'Technical support and assistance',
    },
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Contact Us
            </h1>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Have questions? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Info Cards */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {contactInfo.map((info, index) => (
              <div
                key={index}
                className="p-6 bg-gray-50 rounded-2xl hover:shadow-lg transition-shadow"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center mb-4">
                  <info.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{info.title}</h3>
                {info.details.map((detail, i) => (
                  <p key={i} className="text-gray-600">{detail}</p>
                ))}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Form & Map */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Contact Form */}
            <div className="bg-white rounded-3xl p-8 shadow-lg">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Send us a Message</h2>
              
              {submitted ? (
                <div className="text-center py-12">
                  <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Mail className="w-10 h-10 text-green-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Message Sent!</h3>
                  <p className="text-gray-600 mb-6">
                    Thank you for reaching out. We'll get back to you within 24-48 hours.
                  </p>
                  <button
                    onClick={() => setSubmitted(false)}
                    className="text-blue-600 font-medium hover:text-blue-700"
                  >
                    Send another message
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name *
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        required
                        value={formData.name}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="John Doe"
                      />
                    </div>
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        required
                        value={formData.email}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="john@example.com"
                      />
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                        Phone Number
                      </label>
                      <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="+91 98765 43210"
                      />
                    </div>
                    <div>
                      <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                        Subject *
                      </label>
                      <select
                        id="subject"
                        name="subject"
                        required
                        value={formData.subject}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Select a subject</option>
                        <option value="membership">Membership Inquiry</option>
                        <option value="events">Events</option>
                        <option value="partnership">Partnership</option>
                        <option value="support">Technical Support</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                      Message *
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      required
                      rows={5}
                      value={formData.message}
                      onChange={handleChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="How can we help you?"
                    />
                  </div>
                  
                  <button
                    type="submit"
                    className="w-full flex items-center justify-center px-8 py-4 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors"
                  >
                    Send Message
                    <Send className="ml-2 w-5 h-5" />
                  </button>
                </form>
              )}
            </div>
            
            {/* Department Contacts */}
            <div className="space-y-8">
              <div className="bg-white rounded-3xl p-8 shadow-lg">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Department Contacts</h2>
                <div className="space-y-6">
                  {departments.map((dept, index) => (
                    <div
                      key={index}
                      className="flex items-start p-4 bg-gray-50 rounded-xl hover:bg-blue-50 transition-colors"
                    >
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center mr-4 flex-shrink-0">
                        <dept.icon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{dept.title}</h3>
                        <p className="text-sm text-gray-600 mb-1">{dept.description}</p>
                        <a href={`mailto:${dept.email}`} className="text-blue-600 hover:text-blue-700 font-medium">
                          {dept.email}
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Map Placeholder */}
              <div className="bg-white rounded-3xl p-8 shadow-lg">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Find Us</h2>
                <div className="aspect-video bg-gray-200 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">Map view coming soon</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Contact;
