class ControlPlaneRouter:
    """Route control plane models to the control_plane database alias."""

    app_label = 'control_plane'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'control_plane'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'control_plane'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == self.app_label and obj2._meta.app_label == self.app_label:
            return True
        if obj1._meta.app_label == self.app_label or obj2._meta.app_label == self.app_label:
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == 'control_plane'
        if db == 'control_plane':
            return False
        return None
