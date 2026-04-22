import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, ArrowRight, Users, Calendar, Award, Heart, BookOpen, Globe } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const FALLBACK_PLANS = [
  {
    name: 'Learner',
    yearly_fee: '0.00',
    lifetime_fee: null,
    description: 'Start your journey with ACTIV',
    benefits: ['Access to community events', 'Monthly newsletter', 'Member directory access'],
    is_active: true,
  },
  {
    name: 'Intermediate',
    yearly_fee: '2000.00',
    lifetime_fee: null,
    description: 'For dedicated ACTIV members',
    benefits: ['All Learner benefits', 'Workshop access', 'Priority event registration', 'Certificate of membership'],
    is_active: true,
  },
];

const Membership = () => {
  const [plans, setPlans] = useState(FALLBACK_PLANS);

  useEffect(() => {
    fetch(`${API_URL}/memberships/tiers/`)
      .then((r) => r.json())
      .then((data) => {
        const results = data.results || data;
        if (Array.isArray(results) && results.length > 0) {
          setPlans(results.filter((t) => t.is_active));
        }
      })
      .catch(() => {});
  }, []);

  const benefits = [
    {
      icon: Calendar,
      title: 'Exclusive Events',
      description: 'Access to members-only events, workshops, and networking sessions.',
    },
    {
      icon: Users,
      title: 'Professional Network',
      description: 'Connect with professionals from various industries and backgrounds.',
    },
    {
      icon: BookOpen,
      title: 'Learning Resources',
      description: 'Access to exclusive educational content, webinars, and training materials.',
    },
    {
      icon: Award,
      title: 'Recognition',
      description: 'Get recognized for your contributions with awards and certificates.',
    },
    {
      icon: Heart,
      title: 'Make an Impact',
      description: 'Participate in community initiatives and make a real difference.',
    },
    {
      icon: Globe,
      title: 'Global Community',
      description: 'Connect with members from across the country and beyond.',
    },
  ];

  const faqs = [
    {
      question: 'How do I become a member?',
      answer: 'Simply click on the "Join Now" button and complete the registration form. You\'ll receive a confirmation email with next steps.',
    },
    {
      question: 'What is the membership duration?',
      answer: 'Premium membership is valid for one year from the date of registration. Basic membership is free and valid indefinitely.',
    },
    {
      question: 'Can I upgrade my membership later?',
      answer: 'Yes! You can upgrade from Basic to Premium membership at any time. Contact us for assistance.',
    },
    {
      question: 'What payment methods are accepted?',
      answer: 'We accept all major credit cards, debit cards, UPI, and net banking for premium membership payments.',
    },
    {
      question: 'Is there a refund policy?',
      answer: 'Yes, we offer a 30-day money-back guarantee for premium memberships. If you\'re not satisfied, contact us for a full refund.',
    },
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Membership Plans
            </h1>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Choose the membership plan that best fits your needs and join our growing community.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {plans.map((plan, index) => {
              const isFree = !plan.yearly_fee || parseFloat(plan.yearly_fee) === 0;
              const priceDisplay = isFree ? 'Free' : `₹${parseFloat(plan.yearly_fee).toLocaleString('en-IN')}`;
              const periodDisplay = isFree ? 'forever' : 'per year';
              const isPopular = index === Math.floor(plans.length / 2);
              const features = Array.isArray(plan.benefits)
                ? plan.benefits
                : typeof plan.benefits === 'string'
                  ? plan.benefits.split('\n').filter(Boolean)
                  : [];
              return (
                <div
                  key={plan.id || index}
                  className={`relative bg-white rounded-3xl overflow-hidden ${
                    isPopular ? 'ring-4 ring-blue-600 shadow-2xl' : 'shadow-lg'
                  }`}
                >
                  {isPopular && (
                    <div className="absolute top-0 right-0 bg-blue-600 text-white text-sm font-medium px-4 py-1 rounded-bl-xl">
                      Most Popular
                    </div>
                  )}
                  <div className="p-8">
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                    <p className="text-gray-500 mb-4">{plan.description}</p>
                    <div className="mb-6">
                      <span className="text-4xl font-bold text-gray-900">{priceDisplay}</span>
                      <span className="text-gray-500">/{periodDisplay}</span>
                    </div>
                    <div className="space-y-3 mb-8">
                      {features.map((feature, i) => (
                        <div key={i} className="flex items-start">
                          <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-600">{feature}</span>
                        </div>
                      ))}
                    </div>
                    <Link
                      to="/register"
                      className={`block w-full py-4 rounded-xl font-semibold text-center transition-all ${
                        isPopular
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                      }`}
                    >
                      {isFree ? 'Get Started' : 'Join Now'}
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Membership Benefits
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Unlock exclusive benefits and opportunities with your membership.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className="p-6 bg-gray-50 rounded-2xl hover:bg-blue-50 transition-colors"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center mb-4">
                  <benefit.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{benefit.title}</h3>
                <p className="text-gray-600">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQs */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-lg text-gray-600">
              Have questions? We've got answers.
            </p>
          </div>
          
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-6 shadow-sm"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {faq.question}
                </h3>
                <p className="text-gray-600">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Join Our Community?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Become a member today and start enjoying exclusive benefits and opportunities.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-600 rounded-xl font-semibold text-lg hover:bg-gray-100 transition-all"
          >
            Join Now
            <ArrowRight className="ml-2 w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Membership;
