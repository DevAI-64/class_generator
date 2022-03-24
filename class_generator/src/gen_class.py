"""This module contains GenClass for generate class files."""

import pickle
import os
from typing import Any

from pydash import get  # type: ignore


PATH_TEMPLATES = "src/templates"
PATH_GEN_FILES = "./gen_files"


class GenClass:
    """GenClass is class for generate class files."""

    def __init__(
        self,
        name_file: str,
        attributes: dict,
        methods: dict,
        inherit: str = ""
    ) -> None:
        """Initialize the class and generate the class and tests files.

        Args:
            name_file (str): The name of class file to generate.
            attributes (dict): The dictionary of attributes with format
                {attribute_name: attribute_type}
            methods (dict): The dictionary of methods with format
                {methods_name: list_params_with_type_and_default_values}
            inherit (str, optional): the class from which the generated
                class inherits, by default = "".

        Attributes:
            name_file (str): The name of class file to generate.
            attributes (dict): The dictionary of attributes with format
                {attribute_name: attribute_type}
            methods (dict): The dictionary of methods with format
                {methods_name: list_params_with_type_and_default_values}
            inherit (str, optional): The class from which the generated
                class inherits, by default = "".
            name_class (str): The name of class calculated with name_file.
        """
        self._name_file: str = name_file
        self._attributes: dict = attributes
        self._methods: dict = methods
        self._inherit: str = f"({inherit}):" if inherit else ":"
        self._name_class: str = "".join(
            part_name.capitalize() for part_name in self._name_file.split("_")
        )

        self._gen_class()
        self._gen_unit_tests()

    def _gen_attributes(self) -> Any:
        """Get attribute name and type from python generator.

        Return:
            Any: The name of attribute and the type of attribute.
        """
        for attribute_name, attribute_type in self._attributes.items():
            yield attribute_name, attribute_type

    def _gen_methods(self) -> Any:
        """Get method name and params from python generator.

        Return:
            Any: The name of method and params.
        """
        for method_name, method_params in self._methods.items():
            yield method_name, method_params

    def _set_tab(self, nb_tab: int = 1, spaces_by_tab: int = 4) -> str:
        """Build tabulations with spaces, 4 spaces by tab by default.

        Args:
            nb_tab (int, optional): The number of tabulations, 1 by default.
            spaces_by_tab (int, optional): The number of spaces
                to define tabulation, 4 by default.

        Returns:
            str: The string contains the number of spaces to define.
        """
        return " " * spaces_by_tab * nb_tab

    def _get_accessors(
        self,
        attribute_name: str,
        attribute_type: str
    ) -> str:
        """Get accessors for attribute.

        Args:
            attribute_name (str): The name of attribute.
            attribulte_type (str): The type of attribute.

        Returns:
            str: Accessors from the attribute.
        """
        result: str = ""
        with open(f"{PATH_TEMPLATES}/accessors", "rb") as file:
            result = pickle.load(file).replace(
                "{attribute_name}",
                attribute_name
            ).replace(
                "{attribute_type}",
                attribute_type
            )
        return result

    def _get_attributes_strings(self) -> tuple:
        """Get attributes strings for params, init and docstrings.

        Returns:
            tuple: The strings for params, init and docstrings.
        """
        desc_attr: str = "Explain this attr..."
        attributes_docstring: str = "\n".join(
            f"{self._set_tab(3)}{attr_name} ({attr_type}): {desc_attr}"
            for attr_name, attr_type in self._gen_attributes()
        )
        attributes_params: str = "".join(
            f",\n{self._set_tab(2)}{attr_name}: {attr_type}"
            for attr_name, attr_type in self._gen_attributes()
        )
        attributes_init: str = "\n".join(
            f"{self._set_tab(2)}self._{attr_name}: {attr_type} = {attr_name}"
            for attr_name, attr_type in self._gen_attributes()
        )
        return attributes_docstring, attributes_params, attributes_init

    def _get_class(self) -> str:
        """Get structure of class.

        Returns:
            str: The structure of class with necessary replaces.
        """
        result: str = ""
        (
            attributes_docstring,
            attributes_params,
            attributes_init
        ) = self._get_attributes_strings()
        with open(f"{PATH_TEMPLATES}/class", "rb") as file:
            result = pickle.load(file).replace(
                "{class_name}",
                self._name_class
            ).replace(
                "{attributes_params}",
                attributes_params
            ).replace(
                "{attributes_docstring}",
                attributes_docstring
            ).replace(
                "{attributes_init}",
                attributes_init
            )
        return result

    def _get_methods_strings(self, method_params: list) -> tuple:
        """Get methods strings for params, returns and docstrings.

        Args:
            method_params (list): The list of parameters for method.

        Returns:
            tuple: The strings for params, returns and docstrings.
        """
        returns_string: str = ""
        msg_desc: str = "Explain this..."
        params: dict = self._get_methods_dictionary(method_params)

        return_type: str = get(params, "return.0", "None")
        if return_type != "None":
            returns_string = f"\n\n{self._set_tab(2)}Returns:\n"
            returns_string += f"{self._set_tab(3)}{return_type}: {msg_desc}"

        params_docstring: str = f"\n{self._set_tab(3)}".join(
            f"{k} ({v[0]}): {msg_desc}"
            for k, v in params.items()
            if k != "return"
        )

        method_params_list: str = f",\n{self._set_tab(2)}".join(
            param_name.strip()
            for param_name in method_params[:-1]
        )

        return (
            method_params_list,
            return_type,
            params_docstring,
            returns_string
        )

    def _get_methods_dictionary(self, method_params: list) -> dict:
        """Get dictionary of method's parameters.

        Args:
            method_params (list): The list of parameters for method.

        Returns:
            dict: The dictionary of method's parameters.
        """
        params = {}
        for param in method_params:
            param_split_name_type = param.split(":")
            param_split_type_default_value = get(
                param_split_name_type, 1
            ).split("=")
            param_name = get(param_split_name_type, 0).strip()
            param_type = get(param_split_type_default_value, 0).strip()
            param_default_value = get(
                param_split_type_default_value,
                1
            )
            param_default_value = param_default_value.strip() \
                if param_default_value \
                else param_default_value
            params[param_name] = (param_type, param_default_value)
        return params

    def _get_method(
        self,
        method_name: str,
        method_params: list
    ) -> str:
        """Get signature of method.

        Args:
            method_name (str): The name of method.
            method_params (list): The list of parameters for method.

        Returns:
            str: The signature of method.
        """
        result: str = ""
        (
            method_params_list,
            return_type,
            params_docstring,
            returns_string
        ) = self._get_methods_strings(method_params)
        with open(f"{PATH_TEMPLATES}/methods", "rb") as file:
            result = pickle.load(file).replace(
                "{method_name}",
                method_name
            ).replace(
                "{method_params}",
                method_params_list
            ).replace(
                "{return_type}",
                return_type
            ).replace(
                "{params_docstring}",
                params_docstring
            ).replace(
                "{returns_string}",
                returns_string
            )
        return result

    def _gen_class(self) -> None:
        """Generate class files with config files."""
        self._create_folder_and_init_file(PATH_GEN_FILES)
        with open(f"{PATH_GEN_FILES}/{self._name_file}.py", "w") as file:
            file.write(self._get_class())

            for accesseur in (
                self._get_accessors(attr_name, attr_type)
                for attr_name, attr_type in self._gen_attributes()
            ):
                file.write(accesseur)

            for method in (
                self._get_method(method_name, method_params.split(","))
                for method_name, method_params in self._gen_methods()
            ):
                file.write(method)

    def _create_folder_and_init_file(self, path_folder: str) -> None:
        """Create folder and __init__.py file.

        Args:
            path_folder (str): The path to create folder and file.
        """
        os.makedirs(path_folder, exist_ok=True)
        with open(
            f"{path_folder}/__init__.py",
            "w"
        ) as file:
            file.write("")

    def _get_method_tests(
        self,
        method_name: str,
        method_params: str
    ) -> str:
        """Get the string for methods in class of tests.

        Args:
            method_name (str): The name of method.
            method_params (str): The parameters of method.

        Returns:
            str: The method of test.
        """
        result: str = ""
        params: str = f",\n{self._set_tab(2)}#{self._set_tab()}".join(
            get(param.split(":"), 0)
            for param in method_params.split(",")[:-1]
        )
        with open(
            f"{PATH_TEMPLATES}/methods_tests",
            "rb"
        ) as pickle_file_methods:
            result = pickle.load(
                pickle_file_methods
            ).replace(
                "{method_name}",
                method_name
            ).replace(
                "{class_file}",
                self._name_file
            ).replace(
                "{class_name}",
                self._name_class
            ).replace(
                "{params}",
                params
            )
        return result

    def _get_class_tests(self, methods_for_tests: str) -> str:
        """Get the class of tests.

        Args:
            methods_for_tests (str): Methods for class tests.

        Returns:
            The class of tests.
        """
        result: str = ""
        with open(f"{PATH_TEMPLATES}/tests", "rb") as pickle_file:
            result = pickle.load(pickle_file).replace(
                "{class_name}",
                self._name_class
            ).replace(
                "{methods_for_tests}",
                methods_for_tests
            ).replace(
                "{file_name}",
                self._name_file
            )
        return result

    def _gen_unit_tests(self) -> None:
        """Generate the units tests for class."""
        path_tests: str = f"{PATH_GEN_FILES}/tests_unittest"
        path_assets: str = f"{path_tests}/assets"
        path_file_class_tests: str = f"{path_tests}/test_{self._name_file}.py"
        self._create_folder_and_init_file(path_tests)
        self._create_folder_and_init_file(path_assets)

        with open(path_file_class_tests, "w") as file:
            result_methods: str = "".join(
                self._get_method_tests(method_name, method_params)
                for method_name, method_params in self._methods.items()
            )
            file.write(
                self._get_class_tests(
                    result_methods
                )
            )
