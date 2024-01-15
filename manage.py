# Copyright © Lumenore Inc. All rights reserved.
# This software is the confidential and proprietary information of
# Lumenore Inc. "Confidential Information".
# You shall * not disclose such Confidential Information and shall use it only in
# accordance with the terms of the intellectual property agreement
# you entered into with Lumenore Inc.
# THIS SOFTWARE IS INTENDED STRICTLY FOR USE BY Lumenore Inc.
# AND ITS PARENT AND/OR SUBSIDIARY COMPANIES. Lumenore
# MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE SOFTWARE,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
# Lumenore SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY ANY PARTY AS A RESULT
# OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lumenore_apps.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
