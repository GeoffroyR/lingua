# coding=utf-8

import unittest


class ExtractTests(unittest.TestCase):
    def extract(self, snippet):
        from lingua.extractors.xml import extract_xml
        from StringIO import StringIO
        snippet = StringIO(snippet)
        return list(extract_xml(snippet, None, None, None))

    def test_empty_xml(self):
        self.assertEqual(self.extract("<html/>"), [])

    def test_attributes_plain(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:attributes="title" title="tést title"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "tést title", [])])

    def test_attributes_without_ns(self):
        snippet = """\
                <html>
                  <dummy i18n:translate="">Foo</dummy>
                  <other xmlns:i="http://xml.zope.org/namespaces/i18n"
                         i18n:domain="lingua">
                    <dummy i:translate="">Foo</dummy>
                  </other>
                  <dummy i18n:translate="">Foo</dummy>
                  <dummy i18n:translate="">Foo</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [
                    (2, None, "Foo", []),
                    (5, None, "Foo", []),
                    (7, None, "Foo", []),
                    (8, None, "Foo", []),
                 ])

    def test_attributes_explicitMessageId(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:attributes="title msg_title" title="test tïtle"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "msg_title", [u"Default: test tïtle"])])

    def test_attributes_NoDomain(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n">
                  <dummy i18n:attributes="title" title="test title"/>
                </html>
                """
        self.assertEqual(self.extract(snippet), [])

    def test_attributes_multipleAttributes(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:attributes="title ; alt" title="tést title"
                         alt="test ålt"/>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "tést title", []),
                 (3, None, "test ålt", [])])

    def test_attributes_multipleAttributesWithExplicitMessageId(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:attributes="title msg_title; alt msg_alt"
                         title="test titlé" alt="test ålt"/>
                </html>
                """
        self.assertEqual(sorted(self.extract(snippet)),
                [(3, None, "msg_alt", ["Default: test ålt"]),
                 (3, None, "msg_title", ["Default: test titlé"])])

    def test_translate_minimal(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:translate="">Dummy téxt</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "Dummy téxt", [])])

    def test_translate_explicitMessageId(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy téxt</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "msgid_dummy", ["Default: Dummy téxt"])])

    def test_translate_subelement(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy
                    <strong>text</strong> demø</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "msgid_dummy",
                    ["Default: Dummy <dynamic element> demø"])])

    def test_translate_namedSubelement(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy
                    <strong i18n:name="text">téxt</strong> demø</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "msgid_dummy", ["Default: Dummy ${text} demø"])])

    def test_translate_translatedSubElement(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:translate="msgid_dummy">Dummy
                    <strong i18n:name="text"
                            i18n:translate="msgid_text">téxt</strong>
                    demø</dummy>
                </html>
                """
        self.assertEqual(sorted(self.extract(snippet)),
                [(3, None, "msgid_dummy", ["Default: Dummy ${text} demø"]),
                 (4, None, "msgid_text", ["Default: téxt"])])

    def test_translate_stripExtraWhitespace(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:translate="">Dummy


                  text</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "Dummy text", [])])

    def test_translate_stripTrailingAndLeadingWhitespace(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy i18n:translate="">
                      Dummy text
                  </dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "Dummy text", [])])

    def test_translate_HtmlEntity(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <button i18n:translate="">lock &amp; load&nbsp;</button>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "lock &amp; load&nbsp;", [])])

    def test_ignore_undeclared_namespace(self):
        snippet = """\
                <html xmlns="http://www.w3.org/1999/xhtml"
                      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <tal:block/>
                  <p i18n:translate="">Test</p>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(5, None, "Test", [])])

    def test_ignore_dynamic_message(self):
        snippet = """\
                <html xmlns="http://www.w3.org/1999/xhtml"
                      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <p i18n:translate="">${'dummy'}</p>
                </html>
                """
        self.assertEqual(self.extract(snippet), [])

    def test_translate_underscore_call_with_unicode_arg(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy tal:replace="_(u'foo')">Dummy</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "foo", [])])

    def test_translate_underscore_call_with_str_arg(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy tal:replace='_("foo")'>Dummy</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "foo", [])])

    def test_translate_underscore_call_with_parenthesis(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy tal:replace='_("f (o) o")'>Dummy</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "f (o) o", [])])

    def test_translate_underscore_call_with_default(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy tal:replace='_("foo", default="blah")'>Dummy</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "foo", ['Default: blah'])])

    def test_translate_multiple_underscore_calls(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy \
                tal:replace="multiple(_('foo'), _('blah'))">Dummy</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "foo", []),
                 (3, None, "blah", [])])

    def test_translate_inner_underscore_call(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy>${_("foo")}</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "foo", [])])

    def test_translate_inner_multiple_underscore_calls(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy>${dummy(_("foo"), _("bar"))}</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "foo", []),
                 (3, None, "bar", [])])

    def test_translate_inner_underscore_call_with_default(self):
        snippet = """\
                <html xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                      i18n:domain="lingua">
                  <dummy>${_("foo", default="blah")}>Dummy</dummy>
                </html>
                """
        self.assertEqual(self.extract(snippet),
                [(3, None, "foo", ['Default: blah'])])

    def test_abort_on_invalid_xml(self):
        snippet = """\
                <html>
                  <h2 id=bar>Foo</h2>
                </html>
                """
        self.assertRaises(SystemExit, self.extract, snippet)
