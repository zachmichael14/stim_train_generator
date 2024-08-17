from abc import ABC, abstractmethod
from inspect import signature, Parameter
from typing import Type, List, Dict

import numpy as np
from PySide6 import QtWidgets

class FunctionRegistry:
    """
    This class serves as a registry for custom methods.
    
    Any subclasses of AbstractBaseFunctionClass will be registered here automatically.

    The registry is then used by the front end to allow users to select custom functions for parameter generation.
    """
    _registry = {}

    @classmethod
    def add_class(cls, new_class) -> None:
        """Add a class to the registry."""
        cls._registry[new_class.name] = new_class

    @classmethod
    def get_classes(cls) -> Dict[str, 'Type[AbstractBaseFunctionClass]']:
        """Return the registry."""
        return cls._registry
    
    @classmethod
    def get_class_names(cls) -> List[str]:
        """Return the names of classes in the registry."""
        return cls._registry.keys()
    
    @classmethod
    def get_class(cls, item: str) -> 'Type[AbstractBaseFunctionClass]':
        """Return an uninstantiated class object from the registry."""
        return cls._registry[item]
    

class AbstractBaseFunctionClass(ABC):
    """
    Any newly created functions should subclass this class as it contains
    important methods for interacting with the rest of the application.

    Concrete classes only need to provide a `name` class attribute and a `generation_function()` instance method.
    
    The `name` attribute is what will be displayed to the user when selecting a function.

    The `generation_function()` method should return a numpy array of generated values. A text input will be created and displayed to the user for each parameter in the method definition, labeled with the name of parameter. Any default values provided in the method definition will be 
    populated in the displayed inputs.
    """
    name = None

    def __init_subclass__(cls, **kwargs) -> None:
        """
        When a concrete class is created, add it to the FunctionRegistry.
        """
        super().__init_subclass__(**kwargs)
        FunctionRegistry.add_class(cls)
    
    def __init__(self) -> None:
        self.name = self.__class__.name
        self.widget: Type[QtWidgets.QWidget] = QtWidgets.QWidget()
        self.subwidgets: List[QtWidgets.QWidget] = []

        self.generate_subwidget()
    
    def generate_subwidget(self) -> None:
        """Create a text input subwidget for each parameter of the function."""
        main_layout = QtWidgets.QVBoxLayout()
    
        method_signature = signature(self.generation_function)

        for parameter_name, parameter in method_signature.parameters.items():
            # Build sublayout for each parameter
            layout = QtWidgets.QHBoxLayout()

            label_text = self.get_label_text(parameter_name)
            label = QtWidgets.QLabel(f"{label_text}:")
            layout.addWidget(label)

            parameter_input = QtWidgets.QLineEdit()

             # Set default value if available
            if parameter.default is not Parameter.empty:
                default_value = parameter.default
                parameter_input.setText(str(default_value))

            self.subwidgets.append(parameter_input)
            layout.addWidget(parameter_input)
            main_layout.addLayout(layout)

        self.widget.setLayout(main_layout)
        
    @staticmethod
    def get_label_text(string: str) -> str:
        """
        Remove underscores and capitalize the first letter of each word of a
        given parameter name.
        """
        split = string.split("_")
        capital = [word.capitalize() for word in split]
        label = " ".join(capital)
        return label
    
    @abstractmethod
    def generation_function(self, *args, **kwargs) -> Type[np.ndarray]:
        """This method must be implemented by subclasses."""
        pass
    

class RecruitmentCurveAmplitudes(AbstractBaseFunctionClass):
    name = "Recruitment Curve Amplitudes"

    def generation_function(self,
                            m_threshold: float,
                            m_saturation: float,
                            h_threshold: float,
                            h_saturation: float,
                            ) -> Type[np.ndarray]:
        h_space = [
            h_threshold,
            ((h_saturation-h_threshold) * 0.05 + h_threshold),
            ((h_saturation-h_threshold) * 0.25 + h_threshold),
            ((h_saturation-h_threshold) * 0.50 + h_threshold),
            ((h_saturation-h_threshold) * 0.75 + h_threshold),
            h_saturation
        ]
                
        m_space = [
            m_threshold,
            ((m_saturation-m_threshold) * 0.05 + m_threshold),
            ((m_saturation-m_threshold) * 0.25 + m_threshold),
            ((m_saturation-m_threshold) * 0.50 + m_threshold),
            ((m_saturation-m_threshold) * 0.75 + m_threshold),
            m_saturation
        ]
                            
        h_m_misc = np.array([
             0.5 * m_threshold,
            0.5 * h_threshold,
            1.1 * m_saturation,
            1.1 * h_saturation
        ])
                
        x = np.concatenate((h_space, m_space, h_m_misc), axis=None)
        x.sort()
        return np.vstack((x,x,x)).flatten(order='F')
    

class FWaveAmplitudes(AbstractBaseFunctionClass):
    name = "F-wave Amplitudes"   

    def generation_function(self,
                          motor_threhold: float,
                          modifier: float = 1.25,
                          number_of_pulses: int = 60,
                          ) -> Type[np.ndarray]:
        return np.ones(number_of_pulses) * motor_threhold * modifier
