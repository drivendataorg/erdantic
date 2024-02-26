import logging

package_logger = logging.getLogger("erdantic")
package_logger.addHandler(logging.NullHandler())
logging.basicConfig(level=logging.INFO)
