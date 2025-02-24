from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from wagtail.admin.admin_url_finder import AdminURLFinder
from wagtail.admin.ui import tables
from wagtail.admin.utils import get_latest_str
from wagtail.admin.views.generic import BaseObjectMixin, IndexView
from wagtail.models import DraftStateMixin, ReferenceIndex


class TitleColumn(tables.TitleColumn):
    def get_link_attrs(self, instance, parent_context):
        return {"title": instance["edit_link_title"]}


class UsageView(BaseObjectMixin, IndexView):
    paginate_by = 20
    is_searchable = False
    page_title = gettext_lazy("Usage of")

    def get_object(self):
        object = super().get_object()
        if isinstance(object, DraftStateMixin):
            return object.get_latest_revision_as_object()
        return object

    def get_page_subtitle(self):
        return get_latest_str(self.object)

    def get_queryset(self):
        return ReferenceIndex.get_references_to(self.object).group_by_source_object()

    def get_columns(self):
        return [
            TitleColumn(
                "name",
                label=_("Name"),
                accessor="label",
                get_url=lambda r: r["edit_url"],
            ),
            tables.ReferencesColumn(
                "field",
                label=_("Field"),
                accessor="references",
                get_url=lambda r: r["edit_url"],
            ),
        ]

    def get_table(self, object_list, **kwargs):
        url_finder = AdminURLFinder(self.request.user)
        results = []
        for object, references in object_list:
            row = {"object": object, "references": references}
            row["edit_url"] = url_finder.get_edit_url(object)
            if row["edit_url"] is None:
                row["label"] = _("(Private %(object)s)") % {
                    "object": object._meta.verbose_name
                }
                row["edit_link_title"] = None
            else:
                row["label"] = str(object)
                row["edit_link_title"] = _("Edit this %(object)s") % {
                    "object": object._meta.verbose_name
                }
            results.append(row)
        return super().get_table(results, **kwargs)

    def get_context_data(self, *args, object_list=None, **kwargs):
        return super().get_context_data(
            *args, object_list=object_list, object=self.object, **kwargs
        )
