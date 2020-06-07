import os
import unittest

import httpretty

from pycareer.aggregation.parsers.python_org import PythonOrgJobParser


@httpretty.activate
class TestPythonOrgJobDetailsParser(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        cls.parser = PythonOrgJobParser()
        cls.test_url = 'https://www.python.org/jobs/3032/'

    def test_job_contact_info_with_multiple_links_in_body(self):
        with open(os.path.join(self.test_data_dir, 'python_org_jobs_3032.html')) as fp:
            content = fp.read()
            httpretty.register_uri(method=httpretty.GET, uri=self.test_url, status=200,
                                   content_type='text/html', body=content)
            content = self.parser.parse(self.test_url)
            self.assertEqual(content['country'], 'GB')
            self.assertEqual(content['contact_name'], 'Robert Wright')
            self.assertEqual(content['contact_email'], 'robert.wright@inflowmatix.com')
            self.assertEqual(content['contact_url'], 'https://www.inflowmatix.com/')
            self.assertEqual(content['description'], u'Inflowmatix are on the lookout for an experienced Python Developer to help us\nbuild a robust backend infrastructure focused on delivering analytical\nservices. This will communicate with additional backend infrastructure written\nin Elixir and frontend GUIs.\n\nThe full-time position is office-based (in Southampton, UK) or remote with the\nability to visit the Southampton office one day per week.\n\nEnquiries and applications can be sent to\n[careers@inflowmatix.com](mailto:careers@inflowmatix.com). We would like\ninitially to see what projects you have worked on and what level of experience\nyou have. We would then invite you to chat with us online and eventually to\nvisit us at our Southampton office, to have a longer discussion and meet the\nwider team.\n\n## Restrictions\n\n  * **Telecommuting is OK**\n  * **No Agencies Please**\n\n## About the Company\n\nInflowmatix was founded in 2015 as a spin out from Imperial College London. We\nwork closely with water industry specialists, engineering experts, and world-\nclass academics to bring cutting edge research and technology to water\nutilities around the world that specifically address the challenges in water\nthat we face today. Our technology spans hardware for data acquisition,\nsoftware for data management and visualisation, and advanced analytics.\n\n')

    def test_job_contact_info_with_empty_contact_url(self):
        with open(os.path.join(self.test_data_dir, 'python_org_jobs_3034.html')) as fp:
            content = fp.read()
            httpretty.register_uri(method=httpretty.GET, uri=self.test_url, status=200,
                                   content_type='text/html', body=content)
            content = self.parser.parse(self.test_url)
            self.assertEqual(content['country'], 'US')
            self.assertEqual(content['contact_name'], 'Adam Chao')
            self.assertEqual(content['contact_email'], 'adam.chao@coxinc.com')
            self.assertEqual(content['contact_url'], '')
            self.assertEqual(content['description'], u"The Job Summary: Dealertrack is currently looking for a Lead Software Engineer\nwith experience in related open-source technology stack and exposure to\nSoftware as a Service to join our team.\n\nYour Role: -Design, develop and maintain web-based applications to enhance the\nperformance and reliability of our current applications. -Participate in the\ndevelopment of new industry-leading products using our open-source-based tech\nstack. -Collaborate with other developers on best practices, code reviews,\ninternal tools and process improvements. -Provide technical leadership within\nthe team. -Review, analyze designs, modify, develop, test, document, and\nimplement software applications. -Analyze and resolve complex problems\nassociated with applications systems. Detect, diagnose, and report related\nproblems.\n\n## Restrictions\n\n  * **No telecommuting**\n  * **No Agencies Please**\n\n## Requirements\n\n## About the Company\n\nDealertrack, a Cox Automotive Brand, is currently looking for a Lead Software\nEngineer with 7+ years' experience to join our Engineering team in Lake\nSuccess NY. Our Teams:\n\n")

    def test_job_contact_info_with_empty_contact_name_url(self):
        with open(os.path.join(self.test_data_dir, 'python_org_jobs_2816.html')) as fp:
            content = fp.read()
            httpretty.register_uri(method=httpretty.GET, uri=self.test_url, status=200,
                                   content_type='text/html', body=content)
            content = self.parser.parse(self.test_url)
            self.assertEqual(content['country'], 'GB')
            self.assertEqual(content['contact_name'], None)
            self.assertEqual(content['contact_email'], 'jobs@bromium.com')
            self.assertEqual(content['contact_url'], '')
            self.assertEqual(content['description'], u"Position Summary:\n\nYou will be joining a team to design, engineer, test, and deploy such systems\nat scale that need to deal with millions of clients, both for Bromium's\ncustomers and our OEM partners. You will be enabling users to aggregate\nconfiguration and management information and to view and analyse any attacks\nisolated by the Bromium software.\n\n## About the Company\n\nFor more information visit our website: <http://www.bromium.com>\n\nTo apply:\n\nPlease submit your resume and cover letter to:\n[jobs@bromium.com](mailto:jobs@bromium.com)\n\n")

    def test_job_description_html_removed(self):
        with open(os.path.join(self.test_data_dir, 'python_org_jobs_3039.html')) as fp:
            content = fp.read()
            httpretty.register_uri(method=httpretty.GET, uri=self.test_url, status=200,
                                   content_type='text/html', body=content)
            content = self.parser.parse(self.test_url)
            self.assertEqual(content['country'], 'FR')
            self.assertEqual(content['description'], u"As a member of our software development team, your main task will be to\ndevelop and maintain the new Python version of MANATEE software. Part of the\nwork will consist in converting some of the current Matlab\xae code to the new\nPython oriented object architecture, but you may also develop new models\n(electrical, electromagnetic, structural, acoustic, \u2026) to extend the software\ncapabilities. These new modules will be developed from scratch (UML) together\nwith the R&D engineers.\n\nYou will may also help the other R&D engineers on the internal research\nprogram of EOMYS (max 20% of the time) depending on your skills and\nmotivation.\n\n## About the Company\n\nEOMYS ENGINEERING is a company providing applied research services in\nelectrical engineering, vibro-acoustics and heat transfer with more than 75%\nof its sales out of France. EOMYS outsourced R&D activities include multi-\nphysics modelling, numerical simulation.\n\n")
